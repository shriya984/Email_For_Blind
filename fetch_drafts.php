<?php
$conn = new mysqli('localhost','root','','imails');
if($conn->connect_error) die("DB Error: ".$conn->connect_error);

$user = $_GET['user'] ?? '';

if(isset($_GET['countOnly']) && $_GET['countOnly']==1){
    $stmt = $conn->prepare("SELECT COUNT(*) FROM emails WHERE sender=? AND folder='draft'");
    $stmt->bind_param("s",$user);
    $stmt->execute();
    $stmt->bind_result($count);
    $stmt->fetch();
    echo $count;
    exit;
}

$stmt = $conn->prepare("SELECT id, recipient, subject, message, attachment, created_at FROM emails WHERE sender=? AND folder='draft' ORDER BY created_at DESC");
$stmt->bind_param("s",$user);
$stmt->execute();
$res = $stmt->get_result();

while($row = $res->fetch_assoc()){
    echo "<li>
            <input type='checkbox' class='selectEmail' value='{$row['id']}'>
            <span class='star' data-id='{$row['id']}'>☆</span>
            <b>To:</b> {$row['recipient']}<br>
            <b>Subject:</b> {$row['subject']}<br>
            <b>Message:</b> {$row['message']}<br>
            <small>{$row['created_at']}</small>
          </li>";
}

$stmt->close();
$conn->close();
?>
