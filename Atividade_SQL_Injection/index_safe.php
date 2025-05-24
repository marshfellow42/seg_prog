<?php
session_start();
if (!isset($_SESSION['rate_limit'])) {
    $_SESSION['rate_limit'] = array();
}

if (isset($_GET["user"]) && isset($_GET["password"])) {

    $rate_limit_count = 5;
    $timeout_minutes = 5;

    if (count($_SESSION['rate_limit'], 0) >= $rate_limit_count) {
        if (!isset($_SESSION['timer_start'])) {
            $_SESSION['timer_start'] = time(); // Store current time
        }

        $duration = $timeout_minutes * 60; // 5 minutes in seconds
        $elapsed = time() - $_SESSION['timer_start'];
        $remaining = $duration - $elapsed;

        if ($remaining <= 0) {
            unset($_SESSION['timer_start']);
            unset($_SESSION['rate_limit']);
        } else {
            $minutes = ceil($remaining / 60);
            echo "Por favor, aguarde mais {$minutes} minuto(s) antes de tentar novamente.";
        }
    } else {
        $conexao = mysqli_connect('localhost', 'root', '', 'teste', 3306);

        $stmt = $conexao->prepare("SELECT * FROM usuarios WHERE user=? AND password=?");
        $stmt->bind_param("ss", $_GET["user"], $_GET["password"]);
        $stmt->execute();

        $resultado = $stmt->get_result();

        $ip = $_SERVER['REMOTE_ADDR'];
        if ($ip == '::1') {
            $ip = '127.0.0.1';
        }

        if ($resultado->num_rows > 0) {
            $response["success"] = 1;
            $response["msg"] = "Sucesso! Acesso garantido...";
            unset($_SESSION['rate_limit']);
        } else {
            $response["success"] = 0;
            $response["msg"] = "Erro! Acesso negado...";
            $_SESSION['rate_limit'][] = $ip;
        }

        /*
        echo PHP_EOL;

        print_r($_SESSION['rate_limit']);
        */

        echo json_encode($response, JSON_UNESCAPED_UNICODE);
    }
} else {
    $response["success"] = 0;
    $response["msg"] = "Erro! Parâmetros inválidos ou ausentes...";
    echo json_encode($response, JSON_UNESCAPED_UNICODE);
}
