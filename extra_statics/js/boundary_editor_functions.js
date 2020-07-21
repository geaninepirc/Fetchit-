function change_edit_status() {
    isEdited = !isEdited
    if (isEdited) {
        document.getElementById("create-edit-bounding").value = "Complete"
        document.getElementById("save").disabled= true
    } else {
        document.getElementById("create-edit-bounding").value = "Create/Edit Bounding"
        document.getElementById("save").disabled= false
    }
}

function remove_point() {
    if (boundingPoly.length > 0) {
        boundingPoly.pop()
    }
}

function save_bounding_poly() {
    let loadingMaskDiv = document.getElementById('loading-mask')
    loadingMaskDiv.style.display = 'block'
    let x_min = 1; let y_min = 1; let x_max = 0; let y_max = 0

    boundingPoly.forEach(value => {
        if (value.x < x_min){
            x_min = value.x
        }
        if (value.x > x_max) {
            x_max = value.x
        }
        if (value.y < y_min) {
            y_min = value.y
        }
        if (value.y > y_max) {
            y_max = value.y
        }
    })

    x_min = x_min < 0 ? 0 : x_min; y_min = y_min < 0 ? 0 : y_min
    x_max = x_max > 1 ? 1 : x_max; y_max = y_max > 1 ? 1 : y_max

    console.log([{x: x_min, y: y_min}, {x: x_max, y: y_min}, {x: x_max, y: y_max}, {x: x_min, y: y_max}])

    if (visionPath !== null) {
        fetch(`/api/image-search/reference-image/${refImageId}/`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json;charset=utf-8",
                "Authorization": `JWT ${token}`
            },
            body: JSON.stringify({
                "bounding_poly": [{x: x_min, y: y_min}, {x: x_max, y: y_min}, {x: x_max, y: y_max}, {x: x_min, y: y_max}]
            })
        })
        .then(response => {
            loadingMaskDiv.style.display = 'none'
            if (response.ok) {
                history.back()
            } else {
                alert(response.statusText)
            }
        })
    } else {
        fetch(`/api/image-search/reference-image/${refImageId}/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json;charset=utf-8",
                "Authorization": `JWT ${token}`
            },
            body: JSON.stringify({
                "bounding_poly": [{x: x_min, y: y_min}, {x: x_max, y: y_min}, {x: x_max, y: y_max}, {x: x_min, y: y_max}]
            })
        })
        .then(response => {
            loadingMaskDiv.style.display = 'none'
            if (response.ok) {
                history.back()
            } else {
                alert(response.statusText)
            }
        })
    }
}