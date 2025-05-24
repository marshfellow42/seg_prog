<?php
if (isset($_GET["user"]) && isset($_GET["password"])) {
    $conexao = mysqli_connect('localhost', 'root', '', 'teste', '3306');

    $sql = "SELECT * FROM usuarios WHERE user='" . $_GET["user"] . "' AND password='" . $_GET["password"] . "'";
    $resultado = mysqli_query($conexao, $sql);

    if (mysqli_num_rows($resultado) > 0) {
        $response["success"] = 1;
        $response["msg"] = "Sucesso! Acesso garantido...";
    } else {
        $response["success"] = 0;
        $response["msg"] = "Erro! Acesso negado...";
    }

    echo json_encode($response, JSON_UNESCAPED_UNICODE);
} else {
    $response["success"] = 0;
    $response["msg"] = "Erro! Parâmetros inválidos ou ausentes...";

    echo json_encode($response, JSON_UNESCAPED_UNICODE);
}