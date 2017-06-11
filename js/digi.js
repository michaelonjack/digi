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


function setSelectedMovie() { 
	jQuery('.movie-link').click(function() { 
		var poster = jQuery(this).find('.poster-med');

		jQuery('#form-movie-id').val(poster.attr('movie-id'));
		jQuery('#form-poster-url').val(poster.attr('poster-url'));
		jQuery('#form-movie-title').val(poster.attr('movie-title'));

		jQuery('#form-row').show();
	});
}


function initSearchbar() { 
	jQuery('#results').hide();
	jQuery('#form-row').hide();

	if (jQuery('#movie').length > 0) { 
		jQuery('#movie').keyup(function() { 
			var movie = jQuery('#movie').val();
			var endpoint = 'https://api.themoviedb.org/3/search/movie?api_key=f8bacc22524d435a1476adae350b4d41&query=' + movie;
			
			if (movie.length > 0) {
				jQuery.getJSON(endpoint, function(json) { 
					jQuery('.poster-container a img').each( function(index) { 
						if (json.results.length >= index + 1) { 
							var result = json.results[index];
							
							if (result.poster_path) {
								jQuery(this).attr('movie-title', result.title);
								jQuery(this).attr('movie-id', result.id);
								jQuery(this).attr('poster-url', result.poster_path);
								jQuery(this).siblings().find('.poster-title').text(result.title);
								jQuery(this).attr('src', 'https://image.tmdb.org/t/p/w500/' + result.poster_path);
							} else { 
								// If the image couldn't be loaded, remove the column from the results
								jQuery(this).closest('.poster-column').remove();
							}
						}
					});
					jQuery('#results').show();
				});
			} else { 
				jQuery('#results').hide();
			}
		});
	}
}



jQuery(document).ready( function() {

	//loadMoviePosters();
	initSearchbar();
	setSelectedMovie();

});