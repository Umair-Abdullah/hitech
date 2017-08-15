CREATE TABLE public.ubw_gp_inward_print
(
  id integer NOT NULL,
  gp_id integer,
  create_uid integer,
  create_date timestamp without time zone,
  name character varying NOT NULL,
  CONSTRAINT ubw_gp_inward_print_pkey PRIMARY KEY (id),
  CONSTRAINT ubw_gp_inward_print_gp_id_fkey FOREIGN KEY (gp_id)
      REFERENCES public.ubw_gp_inward (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE SET NULL,
  CONSTRAINT ubw_gp_inward_print_create_uid_fkey FOREIGN KEY (create_uid)
      REFERENCES public.res_users (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE SET NULL
)
WITH (
  OIDS=FALSE
);
ALTER TABLE public.ubw_gp_inward_print
  OWNER TO odoo;
