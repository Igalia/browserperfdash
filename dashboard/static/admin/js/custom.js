(function($) {
    $('#addrowlink').click(function () {
        var metricsTable = document.getElementById("metrics_table");
        var currentIndex = metricsTable.rows.length;
        var currentRow = metricsTable.insertRow(-1);

        var keyBox = document.createElement("input");
        keyBox.setAttribute("name", "key_" + currentIndex);
        keyBox.setAttribute("class", "vTextField");

        var valueBox = document.createElement("input");
        valueBox.setAttribute("name", "value_" + currentIndex);
        valueBox.setAttribute("class", "vTextField");
        valueBox.setAttribute("type", "number");

        var removeLinkContainer = document.createElement("p");
        removeLinkContainer.setAttribute("class", "deletelink-box");

        var removeLink = document.createElement("a");
        removeLink.setAttribute("class","deletelink");

        var removeText = document.createTextNode("remove");
        removeLink.appendChild(removeText);
        removeLinkContainer.appendChild(removeLink);

        var currentCell = currentRow.insertCell(-1);
        currentCell.appendChild(keyBox);
        currentCell = currentRow.insertCell(-1);
        currentCell.appendChild(valueBox);
        currentCell = currentRow.insertCell(-1);
        currentCell.appendChild(removeLinkContainer);

        $('.deletelink').click(function () {
            $(this).closest("tr").remove();
        })
    });
    $('.deletelink-box').click(function () {
        $(this).closest("tr").remove();
    })

})(django.jQuery);