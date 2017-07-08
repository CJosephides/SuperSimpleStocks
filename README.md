# Super Simple Stocks exercise

This is my (Christos Josephides) attempt of the Super Simple Stocks assignment.

I wrote code for Python 3.x, which runs without errors on a clean virtual environment on my machine.

I designed and implemented code to fulfil the stated requirements to my best understanding and interpretation of the problem. I may have made some unwarranted assumptions, since I am not very familiar with terms from finance; these are clearly marked in the code.

## Some remarks

1. I restricted myself to the standard library for this task so this project can be evaluated on a clean virtual environment. In a more realistic scenario, I would probably use external libraries; e.g., pandas for trading time series.

2. I mostly adhered to the PEP8 coding style guidelines. I did not go overboard with docstrings, but I hope everything is clear.

3. I used the standard datetime module for time stamps. It may not be the prettiest, particularly from an end-user perspective; however, it's part of the standard library and works very well for our purposes here. If I were implementing this more generally, I would probably write a friendlier user interface for datetime objects.

4. I implemented stock trades as a namedtuples, which I find are capable light-weight alternatives to classes that are just records. Not everybody is familiar with namedtuples, however, so these could easily be changed to  regular tuples (even dictionaries or classes) without much loss of generality.

5. I wrote some very rudimentary tests (some unit, some not-so-unit) in test_stock.py to check if things work reasonably well.
