const deleteButton = document.querySelectorAll('.delete-button');
var deleteFlag=false;
for (let i = 0; i < deleteButton.length; i++) {
    const btn = deleteButton[i];
    success = true;
    btn.onclick = function (e) {
        const venueId = e.target.dataset['id'];
        fetch('/venues/' + venueId, {
            method: 'DELETE'
        }).then(function(response){
            return response.json();
        }).then(function(jsonResponse){
            deleteFlag = jsonResponse['success'];
            location.reload();
        })
        .catch(function(err){
            alert(err);
        });
    }
}
    
