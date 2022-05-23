const deleteButton = document.querySelectorAll('.delete-button');
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
            console.log(jsonResponse);
            success = jsonResponse['success'];
            console.log(success);
        })
        .catch(function(err){
            alert(err);
        });
    }
}
    
