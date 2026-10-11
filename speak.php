<?php
$file = "speak.txt";

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $text = $_POST['text'] ?? '';
    file_put_contents($file, $text);
    echo "OK";
} else {
    if (file_exists($file)) {
        echo file_get_contents($file);
    } else {
        echo "";
    }
}
?>
