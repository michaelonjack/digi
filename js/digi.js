if (typeof jQuery === 'undefined') {
	throw new Error('JavaScript requires jQuery')
}


function loadMoviePosters() {

	jQuery('.poster-container a img').each( function(index) {
		var currentImage = jQuery(this);
		var title = currentImage.attr('movie-title').trim();
		var endpoint = 'https://api.themoviedb.org/3/search/movie?api_key=f8bacc22524d435a1476adae350b4d41&query=' + title;

		jQuery.getJSON(endpoint, function(json) {
			if (json.results.length > 0) {
				currentImage.attr('src', 'https://image.tmdb.org/t/p/w500/' + json.results[0].poster_path);
			} else {
				currentImage.attr('src', '/images/placeholder.jpg');
			}
		});
	});
}


function initAccountButton() {
	console.log(jQuery('#account-button').html());
	jQuery('#account-button').click( function() {
		console.log('here');
		window.location.replace("/profile");
	});
}


jQuery(document).ready( function() {

	loadMoviePosters();
	initAccountButton();

});