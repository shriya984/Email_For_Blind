<?php
$conn = new mysqli('localhost','root','','imails');
if($conn->connect_error) die("DB Error: ".$conn->connect_error);

$user = $_GET['user'] ?? '';

// Count only (for badges)
if(isset($_GET['countOnly']) && $_GET['countOnly']==1){
    $stmt = $conn->prepare("SELECT COUNT(*) FROM emails WHERE sender=? AND folder='sent'");
    $stmt->bind_param("s",$user);
    $stmt->execute();
    $stmt->bind_result($count);
    $stmt->fetch();
    echo $count;
    exit;
}

// Fetch Sent emails including the 'starred' column
$stmt = $conn->prepare("SELECT id, recipient, subject, message, attachment, created_at, starred 
                        FROM emails WHERE sender=? AND folder='sent' ORDER BY created_at DESC");
$stmt->bind_param("s",$user);
$stmt->execute();
$res = $stmt->get_result();

while($row = $res->fetch_assoc()){
    // Show star based on starred column (0 or 1)
    $star = isset($row['starred']) && $row['starred'] ? '★' : '☆';

    echo "<li>
            <input type='checkbox' class='selectEmail' value='{$row['id']}'>
            <span class='star' data-id='{$row['id']}'>{$star}</span>
            <b>To:</b> {$row['recipient']}<br>
            <b>Subject:</b> {$row['subject']}<br>
            <b>Message:</b> {$row['message']}<br>
            <small>{$row['created_at']}</small>
          </li>";
}

$stmt->close();
$conn->close();
?>
