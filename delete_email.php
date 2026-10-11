<?php
$conn = new mysqli('localhost','root','','imails');
if($conn->connect_error) die("Connection failed: " . $conn->connect_error);

$data = json_decode(file_get_contents('php://input'), true);
$ids = $data['ids'];
$folder = $data['folder'];
$userEmail = $data['user'];

if(!empty($ids)){
    $idsStr = implode(',', array_map('intval', $ids));
    $stmt = $conn->prepare("DELETE FROM emails WHERE id IN ($idsStr) AND folder=? AND (recipient=? OR sender=?)");
    $stmt->bind_param("sss",$folder,$userEmail,$userEmail);
    $stmt->execute();
    echo count($ids)." email(s) deleted.";
} else {
    echo "No emails selected.";
}
?>
