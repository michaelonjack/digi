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
		jQuery('#form-backdrop-url').val(poster.attr('backdrop-url'));
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
								jQuery(this).attr('backdrop-url', result.backdrop_path);
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

	if(jQuery('#movie-search').length > 0) {
		var request = null;
		jQuery('#movie-search').keyup(jQuery.debounce(0, function() { 
			var query = jQuery('#movie-search').val();
			var endpoint = '/ajaxcodesearch?q=' + query;

			var searchResults = [];
			jQuery('#movie-search').autocomplete({source: searchResults});
			if (query.length > 1) {
				// If a previous request is in progress when a new request is made, abort the previous request
				if (request != null) { 
					request.abort();
				}

				request = jQuery.getJSON(endpoint, function(json) {
				
					for (var i=0; i<10 && i<json.results.length; i++) { 
						var result = json.results[i].title;
						searchResults.push(result);
					}
				
					jQuery('#movie-search').autocomplete({source: searchResults});
				});
			} 
		}));
	}
}



function validateMessageForm() { 
	if (jQuery("#messageform").length) {
		jQuery("#messageform").validate({
		    submitHandler: function (form) {
		        jQuery("#confirmModal").modal('show');
		        jQuery('#sendBtn').click(function () {
		            form.submit();
		       });
		    }
		});
	}
}



function validateCodeForm() { 
	if (jQuery("#action-button").length) {
		jQuery("#action-button").validate({
		    submitHandler: function (form) {
		        jQuery("#confirmModal").modal('show');
		        jQuery('#sendBtn').click(function () {
		            form.submit();
		       });
		    }
		});
	}
}



function setCodeDetails() { 
	if (jQuery("#details-trailer").length > 0) { 
		jQuery("#details-trailer").hide();

		var movieid = jQuery("body").attr("movieid");
		var video_base_url = "https://www.youtube.com/embed/";
		var video_options = "?modestbranding=1&autohide=1&showinfo=0&controls=0";
		var imdb_base_url = "https://www.imdb.com/title/";
		var rotten_base_url = "https://www.rottentomatoes.com/m/";
		var video_endpoint = "https://api.themoviedb.org/3/movie/" + movieid + "/videos?api_key=f8bacc22524d435a1476adae350b4d41&language=en-US";
		var movie_endpoint = "https://api.themoviedb.org/3/movie/" + movieid + "?api_key=f8bacc22524d435a1476adae350b4d41&language=en-US";
	
		jQuery.getJSON(video_endpoint, function(json) { 

			if (json.results.length > 0) {
				var video_key = json.results[0].key;
				jQuery('#details-trailer').attr('src', video_base_url + video_key + video_options);
				
				jQuery('#details-trailer').show();
			}
		});

		jQuery.getJSON(movie_endpoint, function(json) { 
			
			if (json) {
				jQuery('#details-synopsis').text(json.overview);
				jQuery('#details-runtime').text(json.runtime + " minutes");
				jQuery('#details-release').text(new Date(json.release_date).toDateString());
				jQuery('#imdb-link').attr('href', imdb_base_url + json.imdb_id);
				jQuery('#rotten-link').attr('href', rotten_base_url + json.title.replace(/[ ·-]/g, "_").replace(/[:'.,!?]/g, ""));
			}
		});
	}
}



jQuery(document).ready( function() {

	initSearchbar();
	setSelectedMovie();
	setCodeDetails();
	validateMessageForm();
	validateCodeForm();

});