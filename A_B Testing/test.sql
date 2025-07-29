 Column Name | Type |
+-------------+------+
| id          | int  |
| salary      | int  |
+-------------+------+

Write a solution to find the second highest distinct salary from the Employee table.
If there is no second highest salary, return null (return None in Pandas).

The result format is in the following example.


-- one to one relationship between id and salary
-- order the salaries descedning order
-- select distinct salaries
-- create a rank for the salaries
-- select when rank is 2
-- if rank 2 does not exist, then return null


-- order the salaries descedning order
-- select distinct salaries

With salary_rank as (
SELECT
salary,
RANK() OVER(ORDER BY salary DESC) as s_rank
FROM Employee)

SELECT
salary
where s_rank = 2


WITH max_removed as (
SELECT
salary
FROM Employee
WHERE salary is NOT max(salary)
ORDER BY salary DESC)

SELECT
max(salary)
from max_removed
