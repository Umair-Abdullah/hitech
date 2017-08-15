CREATE TABLE public.hr_attendance_temp
(
  id integer NOT NULL,
  create_uid integer,
  create_date timestamp without time zone,
  machine_id integer,
  attendance_id integer,
  employee_id integer,
  time_in timestamp without time zone,
  time_out timestamp without time zone,
  flag_one character varying(2),
  flag_two boolean,
  CONSTRAINT hr_attendance_temp_pkey PRIMARY KEY (id)
);
