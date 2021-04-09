-- Notes are all there is
create table note (
	id			integer primary key	autoincrement not null,
	text		text,
	created		date,
	updated	date
);
