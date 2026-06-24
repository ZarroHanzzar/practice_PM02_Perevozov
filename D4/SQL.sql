USE mydb;

/*SELECT * 
FROM блюда;*/

/*SELECT цена > 150
 FROM блюда*/

/*SELECT *
FROM блюда
ORDER BY время_приготовления DESC*/

/*SELECT *
FROM блюда
WHERE Название LIKE 'С%'*/

/*SELECT *
FROM блюда
LIMIT 2*/

/*SELECT блюда.idБлюда, КоличествоИнгридиента
FROM блюда
JOIN состав_блюда ON блюда.idБлюда = состав_блюда.idБлюда*/

/*SELECT *
FROM блюда
JOIN курьеры on блюда.idБлюда = idКурьера
JOIN состав_блюда on idКурьера = состав_блюда.idБлюда*/

/*SELECT блюда.idБлюда, состав_блюда.idБлюда
FROM блюда
LEFT JOIN состав_блюда on блюда.idБлюда = состав_блюда.idБлюда*/

/*SELECT	блюда.idБлюда, КоличествоИнгридиента
FROM блюда
LEFT JOIN состав_блюда ON блюда.idБлюда = состав_блюда.idБлюда
GROUP BY блюда.idБлюда, КоличествоИнгридиента*/

/*SELECT 
    блюда.idБлюда, 
    состав_блюда.КоличествоИнгридиента
FROM блюда
LEFT JOIN состав_блюда ON блюда.idБлюда = состав_блюда.idБлюда
WHERE состав_блюда.idБлюда IS NULL;*/

/*SELECT COUNT(*) AS общее_количество FROM блюда;*/

/*SELECT 
    SUM(Цена) AS сумма_цен,
    MIN(Цена) AS минимальная_цена,
    MAX(Цена) AS максимальная_цена,
    AVG(Цена) AS средняя_цена
FROM блюда
WHERE Цена IS NOT NULL;*/

/*SELECT 
    idРесторана,
    COUNT(*) AS количество_блюд
FROM блюда
WHERE idРесторана IS NOT NULL
GROUP BY idРесторана;*/

/*SELECT 
    idРесторана,
    COUNT(*) AS количество_блюд
FROM блюда
WHERE idРесторана IS NOT NULL
GROUP BY idРесторана
HAVING COUNT(*) > 1;*/

/*SELECT *
FROM блюда
WHERE Цена = (SELECT MAX(Цена) FROM блюда);*/

/*SELECT *
FROM блюда
WHERE idБлюда NOT IN (SELECT DISTINCT idБлюда FROM состав_блюда);*/

/*SELECT *
FROM блюда б
WHERE EXISTS (SELECT 1 FROM состав_блюда сб WHERE сб.idБлюда = б.idБлюда);*/

/*UPDATE блюда 
SET Цена = Цена * 1.10
WHERE Цена IS NOT NULL;*/

/*UPDATE блюда 
SET Название = 'Пицца Маргарита'
WHERE idБлюда = 1;*/

/*DELETE FROM блюда 
WHERE idБлюда IS NULL;*/
