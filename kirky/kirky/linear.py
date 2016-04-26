"""
Our first objective in this module is to be able to 
check to see if for a particular matrix A there is 
vector v s.t. vA = h where h has all positive entries. 

This is essentially asking the question: can we combine 
the rows of A in such a way as to get a row with only 
positive entries? We will call A row-positive

Now we know that the ith entry of h is just the dot 
product of v and the ith column of A. Therefore if 
the columns are c_i we require that if A is m x n
that for all i in [1,n] that dot(c_i, v) >= 0.

Now note that dot(c_i, v) = |c_i||v|cos(theta) therefore
we require that the interior angle between each column and 
v is less than or equal to pi/2. Now if you play around with 
some examples you will quickly realize that this requires that 
we can divide R^m into two pieces using a single hyperplane of 
dimension m - 1 such that all column vectors lie in the same piece.
The hyperplanes that work are orthogonal to the vectors v such that 
vA = h where h has all positive entries.
This is the basis for how we will check to see if a matrix A is 
row-positive.

Now in some sense all we have to do start with two columns. We check to 
see if these two columns are splittable (that is lie in the same piece).
Then we add in a new columns and see if this new combination is still 
splittable. The reason for working in steps is that I think I can come 
up with a simple algorithm for this direction. Here it is:

We take our first two columns. We evaluate the angles these make with 
the axes. We set the smallest in each case to our lower bound and our highest 
to our upper bound. Next, we add pi to each of these angles. We set 
the result of this for the upper bound as a different upper bound and for 
the lower we set it to the lower bound. These bounds are our exclusion bounds.
The first two are just there for the sake of bookkeeping. 

Now when we add in a new vector, we first check its angle with the axes. If 
any of those angles are in the exclusion zone (discounting the very edges of 
that zone). If not then if any of its angles are greater that the ones 
we have kept for bookkeeping we adjust those bounds and the exclusion zone. 

Using this process we will either find a column in an exclusion zone or 
we will end up with those bookkeeping bounds which if we choose a vector 
within those angles, the hyperplane orthogonal to that vector will divide 
our space into two where all of our vectors lie in the same piece. Because of 
this we know that any such vector in those angles will, when multiplied to the 
left of A give us a vector with all positive entries - our positive row.

So not only can we check that A is row-positive, we can find the set of vectors
that give us those positive rows. 
"""

"""
First I have been talking about adding pi to all angles, but we 
all know this can lead to wacky stuff if our angle is already greater 
than pi. So I am going to fix this comparison problem by creating a class
that says 4pi == 2pi
"""

from math import pi

class Angle:
    
    def __init__(self, value):
        self.value = value
        self.canonical = self.getcanonical()
        
    """
    This takes a random angle and turns into its canonical form,
    i.e. between 0 and 2pi
    """
    def getcanonical(self):
        if self.value < 0:
            while self.value < 0:
                self.value += 2 * pi
        else:
            while self.value >= 2 * pi:
                self.value -= 2 * pi
        
    def __add__(self, other):
        return Angle(self.value + other.value)
    
    def __sub__(self, other):
        return Angle(self.value - other.value)
    
    def __mul__(self, scalar):
        return Angle(scalar * self.value)
    
    def __eq__(self, other):
        if self.canonical == other.canonical:
            return True
        else:
            return False
        
    def __gt__(self, other):
        if self.canonical > other.canonical:
            return True
        else:
            return False
    
    def __ge__(self, other):
        if self.canonical >= other.canonical:
            return True
        else:
            return False
        
    def __lt__(self, other):
        if self.canonical < other.canonical:
            return True
        else:
            return False
        
    def __le__(self, other):
        if self.canonical <= other.canonical:
            return True
        else:
            return False
        
    def __hash__(self):
        return hash(self.canonical)
    
    def __repr__(self):
        return str(self)
    
    def __str__(self):
        return str(self.value)
"""
This class takes an upper angle and a lower angle and then looks to check
whether another angle is between them. upper and lower should be Angles
""" 
class Slice:
    
    def __init__(self, upper, lower, closed=True):
        self.upper = lower
        self.lower = upper
        self.closed = closed
        self.ranges = []
        self.setupSlice()
    
    def setupSlice(self):
        if self.upper.canonical < self.lower.canonical:
            self.ranges.append((Angle(0),Angle(self.upper.canonical)))
            self.ranges.append((Angle(self.lower.canonical), Angle(2*pi)))
        else:
            self.ranges.append((Angle(self.lower.canonical),Angle(self.upper.canonical)))
            
    def SetUpper(self, upper):
        self.upper = upper
        self.setupSlice()
        
    def SetLower(self, lower):
        self.lower = lower
        self.setupSlice()
            
    def __contains__(self, angle):
        if not self.closed:
            # we are working with an open interval so we take care of the 
            # edges
            if angle == self.upper or angle == self.lower:
                return False
        # the following behavior is for closed or open intervals
        for bounds in self.ranges:
            if angle >= bounds[0] and angle =< bounds[1]:
                return True
        return False
            
    
"""
Here is the class (and corresponding algorithm) for row-positive checks.
"""

class RowPositive:
    
    def __init__(self, A):
        self.A = A
        self.upper_inclusion = None
        self.lower_inclusion = None
        self.upper_exclusion = None
        self.lower_inclusion = None