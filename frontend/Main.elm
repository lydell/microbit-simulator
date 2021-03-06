module Main exposing (..)

import Dict exposing (Dict)
import Html exposing (Html, div)
import Html.Attributes exposing (style)
import Html.Lazy
import Json.Decode
import Json.Encode
import Keyboard exposing (KeyCode)
import WebSocket


url : String
url =
    "ws://localhost:8000/"


maxX : Int
maxX =
    5


maxY : Int
maxY =
    5


maxBrightness : Int
maxBrightness =
    9


buttonAKeys : List KeyCode
buttonAKeys =
    [ 37, 65 ]


buttonBKeys : List KeyCode
buttonBKeys =
    [ 39, 66 ]


main : Program Never Model Msg
main =
    Html.program
        { init = init
        , update = update
        , subscriptions = subscriptions
        , view = view
        }


type Msg
    = ButtonPressChange Bool ButtonId
    | NoOp
    | WebSocketMsg String


type alias Model =
    { display : Display
    , buttonA : Button
    , buttonB : Button
    }


type alias Display =
    { pixels : Dict PixelCoordinate PixelBrightness
    , isOn : Bool
    }


type alias PixelCoordinate =
    ( Int, Int )


type alias PixelBrightness =
    Int


type alias Pixel =
    ( PixelCoordinate, PixelBrightness )


type alias Button =
    { id : ButtonId
    , isPressed : Bool
    }


type ButtonId
    = A
    | B


type WebSocketData
    = DisplayPixels (List Pixel)
    | DisplayOnOff Bool
    | InitialData WebSocketInitialData


type alias WebSocketInitialData =
    { display : WebSocketInitialDisplayData
    , buttonA : Bool
    , buttonB : Bool
    }


type alias WebSocketInitialDisplayData =
    { pixels : List Pixel
    , isOn : Bool
    }


type WebSocketMessageName
    = BUTTON_CHANGE


initialModel : Model
initialModel =
    { display = { pixels = initialPixels, isOn = True }
    , buttonA = { id = A, isPressed = False }
    , buttonB = { id = B, isPressed = False }
    }


initialPixels : Dict PixelCoordinate PixelBrightness
initialPixels =
    let
        xs =
            (List.range 0 (maxX - 1))

        ys =
            (List.range 0 (maxY - 1))

        coordinates =
            List.concatMap (\x -> List.map ((,) x) ys) xs

        brightness =
            0

        pixels =
            List.map (\coordinate -> ( coordinate, brightness )) coordinates
    in
        Dict.fromList pixels


init : ( Model, Cmd Msg )
init =
    initialModel ! []


update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    case msg of
        ButtonPressChange isPressed id ->
            let
                button =
                    case id of
                        A ->
                            model.buttonA

                        B ->
                            model.buttonB

                ( newButton, command ) =
                    updateButton isPressed button

                newModel =
                    case id of
                        A ->
                            { model | buttonA = newButton }

                        B ->
                            { model | buttonB = newButton }
            in
                newModel ! [ command ]

        NoOp ->
            model ! []

        WebSocketMsg string ->
            updateModelWithWebSocketString string model ! []


updateButton : Bool -> Button -> ( Button, Cmd msg )
updateButton isPressed button =
    let
        newButton =
            { button | isPressed = isPressed }

        command =
            if button.isPressed == isPressed then
                Cmd.none
            else
                WebSocket.send url (encodeButton newButton)
    in
        ( newButton, command )


encodeButton : Button -> String
encodeButton button =
    let
        data =
            [ ( "id", Json.Encode.string (toString button.id) )
            , ( "is_pressed", Json.Encode.bool button.isPressed )
            ]

        payload =
            webSocketPayload BUTTON_CHANGE data
    in
        Json.Encode.encode 0 payload


webSocketPayload :
    WebSocketMessageName
    -> List ( String, Json.Encode.Value )
    -> Json.Encode.Value
webSocketPayload webSocketMessageName data =
    let
        messageName =
            Json.Encode.string (toString webSocketMessageName)
    in
        Json.Encode.object <| ( "message_name", messageName ) :: data


updateModelWithWebSocketString : String -> Model -> Model
updateModelWithWebSocketString string model =
    case Json.Decode.decodeString webSocketMsgDecoder string of
        Err message ->
            let
                _ =
                    Debug.log "Error decoding WebSocket message" message
            in
                model

        Ok webSocketData ->
            updateModelWithWebSocketData webSocketData model


updateModelWithWebSocketData : WebSocketData -> Model -> Model
updateModelWithWebSocketData webSocketData model =
    case webSocketData of
        DisplayPixels pixels ->
            { model | display = updateDisplayPixels pixels model.display }

        DisplayOnOff isOn ->
            { model | display = updateDisplayOnOff isOn model.display }

        InitialData data ->
            { model
                | display =
                    model.display
                        |> updateDisplayPixels data.display.pixels
                        |> updateDisplayOnOff data.display.isOn
                , buttonA = Tuple.first (updateButton data.buttonA model.buttonA)
                , buttonB = Tuple.first (updateButton data.buttonB model.buttonB)
            }


updateDisplayPixels : List Pixel -> Display -> Display
updateDisplayPixels pixels display =
    let
        newPixels =
            Dict.union (Dict.fromList pixels) display.pixels
    in
        { display | pixels = newPixels }


updateDisplayOnOff : Bool -> Display -> Display
updateDisplayOnOff isOn display =
    { display | isOn = isOn }


webSocketMsgDecoder : Json.Decode.Decoder WebSocketData
webSocketMsgDecoder =
    (Json.Decode.field "message_name" Json.Decode.string)
        |> Json.Decode.andThen webSocketMsgDataDecoder


webSocketMsgDataDecoder : String -> Json.Decode.Decoder WebSocketData
webSocketMsgDataDecoder messageName =
    case messageName of
        "DISPLAY_PIXELS" ->
            Json.Decode.map DisplayPixels (Json.Decode.field "pixels" pixelsDecoder)

        "DISPLAY_ON_OFF" ->
            Json.Decode.map DisplayOnOff (Json.Decode.field "is_on" Json.Decode.bool)

        "INITIAL_DATA" ->
            Json.Decode.map InitialData <|
                Json.Decode.map3 WebSocketInitialData
                    (Json.Decode.field "display" displayDecoder)
                    (Json.Decode.field "button_a" Json.Decode.bool)
                    (Json.Decode.field "button_b" Json.Decode.bool)

        _ ->
            Json.Decode.fail ("Unrecognized message_name: " ++ messageName)


pixelsDecoder : Json.Decode.Decoder (List Pixel)
pixelsDecoder =
    Json.Decode.list <|
        Json.Decode.map2 (,)
            (Json.Decode.index 0
                (Json.Decode.map2
                    (,)
                    (Json.Decode.index 0 Json.Decode.int)
                    (Json.Decode.index 1 Json.Decode.int)
                )
            )
            (Json.Decode.index 1 Json.Decode.int)


displayDecoder : Json.Decode.Decoder WebSocketInitialDisplayData
displayDecoder =
    Json.Decode.map2 WebSocketInitialDisplayData
        (Json.Decode.field "pixels" pixelsDecoder)
        (Json.Decode.field "is_on" Json.Decode.bool)


subscriptions : Model -> Sub Msg
subscriptions model =
    Sub.batch
        [ Keyboard.downs (onKeypress True)
        , Keyboard.ups (onKeypress False)
        , WebSocket.listen url WebSocketMsg
        ]


onKeypress : Bool -> KeyCode -> Msg
onKeypress isPressed keyCode =
    if List.member keyCode buttonAKeys then
        ButtonPressChange isPressed A
    else if List.member keyCode buttonBKeys then
        ButtonPressChange isPressed B
    else
        NoOp


view : Model -> Html Msg
view model =
    let
        styles =
            [ ( "position", "fixed" )
            , ( "top", "50%" )
            , ( "left", "50%" )
            , ( "transform", "translate(-50%, -50%)" )
            , ( "width", "90vmin" )
            , ( "height", "90vmin" )
            , ( "background-color", "black" )
            ]

        innerStyles =
            if model.display.isOn then
                []
            else
                [ ( "opacity", "0" ) ]
    in
        div [ style styles ]
            [ div [ style innerStyles ]
                (List.map
                    (Html.Lazy.lazy viewPixel)
                    (Dict.toList model.display.pixels)
                )
            ]


viewPixel : Pixel -> Html Msg
viewPixel pixel =
    let
        ( ( x, y ), brightness ) =
            pixel

        top =
            (100 / (toFloat maxY)) * ((toFloat y) + 0.5)

        left =
            (100 / (toFloat maxX)) * ((toFloat x) + 0.5)

        alpha =
            toFloat brightness / toFloat maxBrightness

        styles =
            [ ( "position", "absolute" )
            , ( "top", (toString top) ++ "%" )
            , ( "left", (toString left) ++ "%" )
            , ( "transform", "translate(-50%, -50%)" )
            , ( "width", "10%" )
            , ( "height", "10%" )
            , ( "background-color"
              , "rgba(255, 0, 0, " ++ (toString alpha) ++ ")"
              )
            ]
    in
        div [ style styles ]
            []
