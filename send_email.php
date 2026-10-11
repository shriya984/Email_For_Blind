<?php
use PHPMailer\PHPMailer\PHPMailer;
use PHPMailer\PHPMailer\Exception;
require 'vendor/autoload.php';

// DB connection
$conn = new mysqli('localhost','root','','imails');
if ($conn->connect_error) die("DB Error: ".$conn->connect_error);

// Only handle POST requests
if($_SERVER['REQUEST_METHOD'] != 'POST'){
    die("Invalid request");
}

// Required fields
$recipient = $_POST['recipient'] ?? ($_POST['to'] ?? '');
$subject   = $_POST['subject'] ?? '';
$body      = $_POST['message'] ?? '';
$sender    = $_POST['sender'] ?? 'shriyajedhe984@gmail.com';

if(!$recipient || !$subject || !$body){
    echo "<script>
            alert('Missing required fields');
            speechSynthesis.speak(new SpeechSynthesisUtterance('Missing required fields. Please fill all fields and try again.'));
            window.history.back();
          </script>";
    exit;
}

// PHPMailer
$mail = new PHPMailer(true);
try {
    $mail->isSMTP();
    $mail->Host = 'smtp.gmail.com';
    $mail->SMTPAuth = true;
    $mail->Username = $sender;
    $mail->Password = 'usyz zvga gcyv yanp';
    $mail->SMTPSecure = 'tls';
    $mail->Port = 587;

    $mail->setFrom($sender,'Shriya Jedhe');
    $mail->addAddress($recipient);

    $fileName = null;
    if(isset($_FILES['attachment']) && $_FILES['attachment']['error']==0){
        if(!is_dir('uploads')) mkdir('uploads',0777,true);
        $fileName = time().'_'.basename($_FILES['attachment']['name']);
        move_uploaded_file($_FILES['attachment']['tmp_name'], "uploads/".$fileName);
        $mail->addAttachment("uploads/".$fileName);
    }

    $mail->isHTML(true);
    $mail->Subject = $subject;
    $mail->Body = $body;

    if($mail->send()){
        // Insert Sent
        $stmt = $conn->prepare("INSERT INTO emails (sender, recipient, subject, message, attachment, folder) VALUES (?,?,?,?,?,'sent')");
        $stmt->bind_param("sssss",$sender,$recipient,$subject,$body,$fileName);
        $stmt->execute();

        // Insert Inbox
        $stmt2 = $conn->prepare("INSERT INTO emails (sender, recipient, subject, message, attachment, folder) VALUES (?,?,?,?,?,'inbox')");
        $stmt2->bind_param("sssss",$sender,$recipient,$subject,$body,$fileName);
        $stmt2->execute();

        $stmt->close();
        $stmt2->close();

        // ✅ Alert + TTS + redirect
        echo "<script>
                alert('Email sent and stored in DB!');
                speechSynthesis.speak(new SpeechSynthesisUtterance('Your email was sent successfully and stored in database.'));
                window.location.href = 'compose.html';
              </script>";
    } else {
        echo "<script>
                alert('Mailer Error: ".addslashes($mail->ErrorInfo)."');
                speechSynthesis.speak(new SpeechSynthesisUtterance('Failed to send email. Please try again.'));
                window.history.back();
              </script>";
    }

} catch(Exception $e){
    echo "<script>
            alert('Mailer Exception: ".addslashes($mail->ErrorInfo)."');
            speechSynthesis.speak(new SpeechSynthesisUtterance('An error occurred while sending email.'));
            window.history.back();
          </script>";
}

$conn->close();
?>
