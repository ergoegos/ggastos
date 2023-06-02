-- ENTIDADES



CREATE TABLE customer (
    username VARCHAR PRIMARY KEY, 
    email VARCHAR,
    full_name VARCHAR,
    password_hash VARCHAR,
    sheet_id VARCHAR,
    credentials JSON
);

CREATE TABLE months (

    id INTEGER PRIMARY KEY,
    month_name VARCHAR

);


CREATE TABLE expense (
	id SERIAL PRIMARY KEY,
    concept VARCHAR,
	amount FLOAT,
	subconcept VARCHAR,
	month_id INTEGER,
	username VARCHAR,
    FOREIGN KEY (month_id) REFERENCES months (id),
	FOREIGN KEY (username) REFERENCES customer (username)
);


CREATE TABLE income (
    concept VARCHAR,
	amount FLOAT,
	subconcept VARCHAR,
	month_id INTEGER,
    username VARCHAR,
    FOREIGN KEY (month_id) REFERENCES months (id),
	FOREIGN KEY (username) REFERENCES customer (username)
);


CREATE TABLE income_projection (
    concept VARCHAR,
	amount FLOAT,
	month_id INTEGER,
    username VARCHAR,
    FOREIGN KEY (month_id) REFERENCES months (id),
	FOREIGN KEY (username) REFERENCES customer (username)
);


CREATE TABLE expense_projection (
 
    concept VARCHAR,
	amount FLOAT,
	month_id INTEGER,
    username VARCHAR,
    FOREIGN KEY (month_id) REFERENCES months (id),
	FOREIGN KEY (username) REFERENCES customer (username)
);




CREATE TABLE saving_projection (
	id SERIAL PRIMARY KEY,
    amount FLOAT,
	month_id INTEGER,
	username VARCHAR,
    FOREIGN KEY (month_id) REFERENCES months (id),
	FOREIGN KEY (username) REFERENCES customer (username)
);




INSERT INTO public.months (id, month_name)
VALUES
    (1, 'Enero'),
    (2, 'Febrero'),
    (3, 'Marzo'),
    (4, 'Abril'),
    (5, 'Mayo'),
    (6, 'Junio'),
    (7, 'Julio'),
    (8, 'Agosto'),
    (9, 'Septiembre'),
    (10, 'Octubre'),
    (11, 'Noviembre'),
    (12, 'Diciembre');


-- VISTAS

CREATE VIEW monthly_expenses AS  
WITH expenses_cte AS (
        SELECT ex_1.username,
            mt.month_name AS month_name,
            sum(ex_1.amount) AS amount
        FROM expense ex_1
             JOIN months mt ON ex_1.month_id = mt.id
        GROUP BY ex_1.username, mt.id, mt.month_name
        ORDER BY mt.id
        ), projection_cte AS (
        SELECT pj_1.username,
            mt.month_name AS month_name,
            sum(pj_1.amount) AS amount_expected
        FROM expense_projection pj_1
        JOIN months mt ON pj_1.month_id = mt.id
        GROUP BY pj_1.username, mt.id, mt.month_name
        ORDER BY mt.id
        )
 SELECT ex.month_name,
    ex.amount,
    pj.amount_expected,
    ex.username
FROM expenses_cte ex
JOIN projection_cte pj ON ex.username::text = pj.username::text AND ex.month_name::text = pj.month_name::text;


CREATE VIEW monthly_expenses_by_concept AS
 SELECT ex.username,
    mt.month_name AS month_name,
    ex.concept,
    sum(ex.amount) AS amount
   FROM expense ex
     JOIN months mt ON ex.month_id = mt.id
  GROUP BY ex.username, mt.id, mt.month_name, ex.concept
  ORDER BY mt.id;


CREATE VIEW monthly_incomes AS
   WITH incomes_cte AS (
         SELECT inc.username,
            mt.month_name AS month_name,
            sum(inc.amount) AS amount
           FROM income inc
             JOIN months mt ON inc.month_id = mt.id
          GROUP BY inc.username, mt.id, mt.month_name
          ORDER BY mt.id
        ), projection_cte AS (
         SELECT pj_1.username,
            mt.month_name AS month_name,
            sum(pj_1.amount) AS amount_expected
           FROM income_projection pj_1
             JOIN months mt ON pj_1.month_id = mt.id
          GROUP BY pj_1.username, mt.id, mt.month_name
          ORDER BY mt.id
        )
 SELECT incom.month_name,
    incom.amount,
    pj.amount_expected,
    incom.username
   FROM incomes_cte incom
     JOIN projection_cte pj ON incom.username::text = pj.username::text AND incom.month_name::text = pj.month_name::text;


CREATE VIEW monthly_incomes_by_concept AS
 SELECT inc.username,
    mt.month_name AS month_name,
    inc.concept,
    sum(inc.amount) AS amount
   FROM income inc
     JOIN months mt ON inc.month_id = mt.id
  GROUP BY inc.username, mt.id, mt.month_name, inc.concept
  ORDER BY mt.id;


CREATE VIEW monthly_savings AS
   WITH gastos AS (
         SELECT expense.month_id,
            sum(expense.amount) AS gastos_mensuales,
            expense.username
           FROM expense
          GROUP BY expense.month_id, expense.username
        ), ingresos AS (
         SELECT income.month_id,
            sum(income.amount) AS ingresos_mensuales,
            income.username
           FROM income
          GROUP BY income.month_id, income.username
        ), months AS (
         SELECT months.id,
            months.month_name
           FROM public.months
          ORDER BY months.id
        )
 SELECT mt.month_name AS month_name,
    gs.gastos_mensuales,
    i.ingresos_mensuales,
    i.ingresos_mensuales - gs.gastos_mensuales AS ahorro_mensual,
    sa.amount AS ahorro_esperado,
    gs.username
   FROM gastos gs
     JOIN ingresos i ON gs.month_id = i.month_id AND gs.username::text = i.username::text
     JOIN months mt ON i.month_id = mt.id AND gs.username::text = i.username::text
     JOIN saving_projection sa ON gs.month_id = sa.month_id AND gs.username::text = sa.username::text;