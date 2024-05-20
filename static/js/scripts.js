$(document).ready(function() {
    $('#uploadForm').on('submit', function(event) {
        event.preventDefault();
        var formData = new FormData(this);
        
        $.ajax({
            xhr: function() {
                var xhr = new window.XMLHttpRequest();
                xhr.upload.addEventListener('progress', function(evt) {
                    if (evt.lengthComputable) {
                        var percentComplete = evt.loaded / evt.total;
                        $('#progress').show();
                        $('#progress .progress-bar').css({
                            width: percentComplete * 100 + '%'
                        });
                    }
                }, false);
                return xhr;
            },
            type: 'POST',
            url: '/process_titles',
            data: formData,
            processData: false,
            contentType: false,
            success: function(data) {
                $('#progress').hide();
                var resultsHtml = '<h1 class="text-center">Organized Book Titles</h1>';
                $.each(data, function(cluster_id, books) {
                    resultsHtml += '<div class="card mt-4">';
                    resultsHtml += '<div class="card-header"><h2>Cluster ' + cluster_id + '</h2></div>';
                    resultsHtml += '<div class="card-body"><div class="row">';
                    $.each(books, function(index, book) {
                        resultsHtml += '<div class="col-md-4">';
                        resultsHtml += '<div class="card mb-4 shadow-sm">';
                        resultsHtml += '<img src="' + book.Image_URL + '" class="card-img-top" alt="Book Image">';
                        resultsHtml += '<div class="card-body">';
                        resultsHtml += '<h5 class="card-title">' + book.Title + '</h5>';
                        resultsHtml += '<p class="card-text">' + book.Description + '</p>';
                        resultsHtml += '<p class="card-text"><small class="text-muted">Genres: ' + book.Genres.join(', ') + '</small></p>';
                        resultsHtml += '<p class="card-text"><small class="text-muted">Rating: ' + book.Rating + '</small></p>';
                        resultsHtml += '<p class="card-text"><small class="text-muted">Total Raters: ' + book.Total_Raters + '</small></p>';
                        resultsHtml += '<a href="' + book.Book_URL + '" target="_blank" class="btn btn-primary">View on Goodreads</a>';
                        resultsHtml += '</div></div></div>';
                    });
                    resultsHtml += '</div></div></div>';
                });
                $('#results').html(resultsHtml);
            },
            error: function(xhr, status, error) {
                $('#progress').hide();
                alert('An error occurred: ' + error);
            }
        });
    });
});
