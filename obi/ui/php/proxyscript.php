<?php

$ch = curl_init($_POST["url"]);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
$response = curl_exec($ch);
curl_close($ch);

print $response
?>
