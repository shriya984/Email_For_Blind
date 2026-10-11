<?php
$conn = new mysqli('localhost','root','','imails');
if($conn->connect_error) die("DB Error: ".$conn->connect_error);

$data = json_decode(file_get_contents('php://input'), true);
$id = $data['id'] ?? 0;

if($id){
    // Toggle starred
    $stmt = $conn->prepare("UPDATE emails SET starred = NOT starred WHERE id=?");
    $stmt->bind_param("i",$id);
    $stmt->execute();

    // Return new value
    $stmt = $conn->prepare("SELECT starred FROM emails WHERE id=?");
    $stmt->bind_param("i",$id);
    $stmt->execute();
    $stmt->bind_result($starred);
    $stmt->fetch();
    echo $starred; // 1 or 0
}

$conn->close();
?>
