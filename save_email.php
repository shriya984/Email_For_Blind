<?php
$conn = new mysqli('localhost','root','','imails');
if ($conn->connect_error) die("DB Error: ".$conn->connect_error);

if($_SERVER['REQUEST_METHOD'] != 'POST'){
    die("Invalid request");
}

// Get form data
$sender    = $_POST['sender'] ?? 'shriyajedhe984@gmail.com';
$recipient = $_POST['to'] ?? '';
$subject   = $_POST['subject'] ?? '';
$body      = $_POST['message'] ?? '';
$fileName  = null;

// Handle attachment
if(isset($_FILES['attachment']) && $_FILES['attachment']['error'] == 0){
    if(!is_dir('uploads')) mkdir('uploads',0777,true);
    $fileName = time().'_'.basename($_FILES['attachment']['name']);
    move_uploaded_file($_FILES['attachment']['tmp_name'], "uploads/".$fileName);
}

$stmt = $conn->prepare("INSERT INTO emails (sender, recipient, subject, message, attachment, folder) VALUES (?,?,?,?,?, 'draft')");
$stmt->bind_param("sssss", $sender, $recipient, $subject, $body, $fileName);
$stmt->execute();
$stmt->close();
$conn->close();

echo "Draft saved successfully!";
?>
