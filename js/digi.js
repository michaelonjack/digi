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


function initSearchbar() { 
	jQuery('#results').hide();
	if (jQuery('.searchbar').length > 0) { 
		jQuery('.searchbar').keyup(function() { 
			var movie = jQuery('.searchbar').val();
			var endpoint = 'https://api.themoviedb.org/3/search/movie?api_key=f8bacc22524d435a1476adae350b4d41&query=' + movie;
			
			if (movie.length > 0) {
				jQuery.getJSON(endpoint, function(json) { 
					jQuery('.poster-container a img').each( function(index) { 
						if (json.results.length >= index + 1) { 
							var result = json.results[index];
							
							if (result.poster_path) {
								jQuery(this).attr('movie-title', result.title);
								jQuery(this).siblings().find('.poster-title').text(result.title);
								jQuery(this).attr('src', 'https://image.tmdb.org/t/p/w500/' + result.poster_path);
							} else { 
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

	loadMoviePosters();
	initSearchbar();

	jQuery(document).on('error', 'img', function() {console.log('hi');});

});