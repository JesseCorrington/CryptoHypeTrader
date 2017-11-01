console.log("starting client app");

$.getJSON("/api/prices", (ret) => {
    console.log(ret);
});