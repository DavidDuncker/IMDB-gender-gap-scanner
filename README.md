# IMDB-gender-gap-scanner
In the wake of the Ghostbusters controversy and the highly gendered reviews of the movie on IMDB, 
this code will scan IMDB and gather a database of gender gaps in various movies to compare against the 
Ghostbusters remake.

The code uses Python and MySQL. It creates a database called "imdb_stuff", and two tables: "top_titles" and 
"gender_ratings".

The function grab_top_rated_titles(total_entries) scans IMDB for a list of movies (denoted by the variable total_entries)
sorted by the total number of rating votes, and enters the movie's IMDB id (i.e. "tt1289401"), movie title, and number of 
votes into the "top_titles" table.

The function scan_gender_disparities() loads all the movies from "top_titles", scans IMDB for 1) Release year, 2) Number of 
votes for each rating (1-10), separated by each gender, and 3) Percentage of votes for each rating (1-10), separated by gender
(i.e. "Number of men who rated Ghostbusters as a '1', number of women who rated Ghostbusters as a '1', percent of men who rated 
Ghostbusters as a '1', and so forth). The function then calculated the mean vote for each gender, the variance of the vote within
each gender, the difference between the number of men who rated the movie a '1' vs the number of women who rated the movie a '1', 
the difference between the number of men who rated the movie a '10' vs the number of women who rated the movie a '10',  and 
the difference between the male mean vote and the female mean vote.

Future modifications will be made when I figure out how to visualize all this data.
