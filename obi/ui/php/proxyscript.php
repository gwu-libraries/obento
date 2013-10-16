<?php

$ch = curl_init($_POST["url"]);
$post_params["q"] = $_POST["q"];
curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
$response = curl_exec($ch);
curl_close($ch);

print $response
?>
