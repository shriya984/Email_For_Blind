<?php
$conn = new mysqli('localhost','root','','imails');
if($conn->connect_error) die("Connection failed: " . $conn->connect_error);

// Get current user
$userEmail = isset($_GET['user']) ? $_GET['user'] : 'shriyajedhe984@gmail.com';

// Count only
if(isset($_GET['countOnly'])){
    $stmt = $conn->prepare("SELECT COUNT(*) FROM emails WHERE recipient=? AND folder='inbox'");
    $stmt->bind_param("s",$userEmail);
    $stmt->execute();
    $stmt->bind_result($count);
    $stmt->fetch();
    echo $count;
    $stmt->close();
    $conn->close();
    exit;
}

// Fetch inbox emails
$stmt = $conn->prepare("SELECT id, sender, recipient, subject, message, created_at, starred FROM emails WHERE recipient=? AND folder='inbox' ORDER BY created_at DESC");
$stmt->bind_param("s",$userEmail);
$stmt->execute();
$result = $stmt->get_result();

while($row = $result->fetch_assoc()){
    $star = $row['starred'] ? '★' : '☆';
    echo "<li>
            <input type='checkbox' class='selectEmail' value='{$row['id']}'>
            <span class='star' data-id='{$row['id']}'>{$star}</span>
            <b>From:</b> {$row['sender']}<br>
            <b>Subject:</b> {$row['subject']}<br>
            <b>Message:</b> {$row['message']}<br>
            <small>{$row['created_at']}</small>
          </li>";
}

$stmt->close();
$conn->close();
?>
