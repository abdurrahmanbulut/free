// Initialize Firebase
firebase.initializeApp({
  apiKey: "AIzaSyCrpHaXnjUGqMVyHPEXn8UuXr3Wbg2VGRw",
  authDomain: "message-2e4ae.firebaseapp.com",
  projectId: "message-2e4ae",
});

// Initialize Cloud Firestore
const db = firebase.firestore();

// Get references to the message form and messages list
const messageForm = document.getElementById("message-form");
const messageInput = document.getElementById("message-input");
const messagesList = document.getElementById("messages-list");
const submitButton = document.getElementById("submit-button");
const activity = document.getElementById("activity");

// Listen for form submit
submitButton.addEventListener("click", (event) => {
  console.log("form submitted");
  event.preventDefault();

  // Get the current user's display name
  const username = firebase.auth().currentUser.displayName;

  // Get the message input value
  const message = messageInput.value;

  // Add the message to the database
  db.collection("messages")
    .add({
      username: username,
      message: message,
      timestamp: firebase.firestore.FieldValue.serverTimestamp(),
    })
    .then(function () {
      console.log("Message added successfully!");
      messageInput.value = "";
    })
    .catch(function (error) {
      console.error("Error writing message: ", error);
    });
});

var username = "nobody";
firebase.auth().onAuthStateChanged(function (user) {
  if (user) {
    // User is signed in.
    const displayName = user.email;
    username = displayName.substring(0, displayName.indexOf("@"));

    // Update the UI to display the username
    const usernameDisplay = document.getElementById("username");
    usernameDisplay.textContent = username;
  } else {
    // No user is signed in.
  }
});

// Listen for real-time updates to the messages list
db.collection("messages")
  .orderBy("timestamp", "desc")
  .onSnapshot(function (snapshot) {
    snapshot.docChanges().forEach(function (change) {
      if (change.type === "added") {
        const li = document.createElement("li");
        console.log(change.doc.data());
        li.textContent = `${change.doc.data().username}: ${change.doc.data().message}`;
        messagesList.appendChild(li);
      }
    });
  });
