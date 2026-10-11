<?php
$conn = new mysqli('localhost', 'root', '', 'imails');
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

$email = isset($_POST['email']) ? $_POST['email'] : '';
$password = isset($_POST['password']) ? $_POST['password'] : '';

if (!$email || !$password) {
    die("Both email and password are required.");
}

$stmt = $conn->prepare("SELECT password FROM users WHERE email=?");
$stmt->bind_param("s", $email);
$stmt->execute();
$stmt->bind_result($hashed_password);
if ($stmt->fetch()) {
    if (password_verify($password, $hashed_password)) {
        echo "Login successful!";
    } else {
        echo "Invalid password.";
    }
} else {
    echo "Email not found.";
}

$stmt->close();
$conn->close();
?>
