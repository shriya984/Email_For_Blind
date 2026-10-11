<?php
$conn = new mysqli('localhost','root','','imails');
if($conn->connect_error) die("DB Error: ".$conn->connect_error);

$user = $_GET['user'] ?? '';
$folder = $_GET['folder'] ?? ''; // optional: 'inbox' or 'sent'

// Count only
if(isset($_GET['countOnly']) && $_GET['countOnly']==1){
    $stmt = $conn->prepare("SELECT COUNT(*) FROM emails WHERE (recipient=? OR sender=?) AND starred=1");
    $stmt->bind_param("ss",$user,$user);
    $stmt->execute();
    $stmt->bind_result($count);
    $stmt->fetch();
    echo $count;
    exit;
}

// Fetch starred emails
$query = "SELECT id, sender, recipient, subject, message, attachment, created_at, folder, starred 
          FROM emails 
          WHERE (recipient=? OR sender=?) AND starred=1";

$stmt = $conn->prepare($query);
$stmt->bind_param("ss",$user,$user);
$stmt->execute();
$res = $stmt->get_result();

while($row = $res->fetch_assoc()){
    $star = $row['starred'] ? '★' : '☆';
    $toFrom = $row['folder']=='sent' ? "To: {$row['recipient']}" : "From: {$row['sender']}";
    echo "<li>
            <input type='checkbox' class='selectEmail' value='{$row['id']}'>
            <span class='star' data-id='{$row['id']}'>{$star}</span>
            <b>{$toFrom}</b><br>
            <b>Subject:</b> {$row['subject']}<br>
            <b>Message:</b> {$row['message']}<br>
            <small>{$row['created_at']}</small>
          </li>";
}

$stmt->close();
$conn->close();
?>
