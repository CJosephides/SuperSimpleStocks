# Super Simple Stocks exercise



# Some remarks

1. I restricted myself to the standard library for this task so that this assignment can be evaluated on a clean virtual environment.
In a more realistic scenario, I would probably use external libraries; e.g., pandas for trading time series.
... 
2. I mostly adhered to PEP8 guidelines; however, I violated the 80 character/line rule when this improves readability.

3. I used datetime for time stamps. It may not be the prettiest, particularly 
from an end-user perspective, but it's part of the standard library and works 
very well for our purposes here. If I were implementing this more generally, 
I would probably write a friendlier user interface for datetime objects.

4. I implemented stock trades as a namedtuples, which I find are capable 
light-weight alternatives to classes that are just records. Not everybody is 
familiar with namedtuples, however, so these could easily be changed to 
regular tuples.
