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

from math import pi
    
class Slice:
    
    def __init__(self, angle1, angle2, closed=True):
        self.WAITING_FOR_ORIENTATION = False
        self.angles = [angle1, angle2]
        self.lower = None
        self.upper = None
        # now we set the two bounds
        self.inclusion_bounds = self.getSliceBounds(angle1, angle2)
        self.exclusion_bounds = self.getSliceBounds(self.getOppositeAngle(angle1), self.getOppositeAngle(angle2))
        
    def rotateTo(self, angle1, angle2, clockwise):
        # this sees how many radians are needed to rotate angle1 to 
        # angle2 clockwise or counterclockwise depending on the value 
        # of the clockwise input
        if angle1 == angle2:
            return 0
        if not clockwise:
            if angle2 < angle1:
                return (2 * pi - angle1) + angle2
            elif angle1 < angle2:
                return angle2 - angle1
        else:
            if angle2 < angle1:
                return angle1 - angle2
            elif angle1 < angle2:
                return angle1 + (2 * pi - angle2)
    """
    here we need to find the internal angle and then 
    set the bounds based off of that finding. To do so we will
    check to see if angle1 rotates to angle2 faster through a 
    clockwise or counter clockwise direction. If it is clockwise 
    we go ahead and set angle2 to what is our lower bound (taking
    care of the case where the interior angle contains the axis we 
    are taking the angle from). In the other case we do the opposite
    (also taking care of the complication.
    
    Note that there is one complicated case, and that is where they 
    are equal. Then we need to wait until we try to add in a new vector
    to choose the orientation of the 'interior' angle
    """       
    def getSliceBounds(self, angle1, angle2):
        bounds = []
        clockwise = self.rotateTo(angle1, angle2, True)
        counter_clockwise = self.rotateTo(angle1, angle2, False)
        if clockwise < counter_clockwise:
            self.lower = angle2
            self.upper = angle1
            if self.upper < self.lower:
                self.bounds.append((self.lower, 2*pi))
                self.bounds.append((0,self.upper))
            else:
                self.bounds.append(self.lower, self.upper)
        elif counter_clockwise < clockwise:
            self.lower = angle1
            self.upper = angle2
            if self.upper < self.lower:
                self.bounds.append((self.lower, 2*pi))
                self.bounds.append((0,self.upper))
            else:
                self.bounds.append(self.lower, self.upper)
        else:
            # in this case they are equal so we need to wait for an 
            # orientation
            self.WAITING_FOR_ORIENTATION = True
        return bounds
            
    def getOppositeAngle(self, angle):
        angle = angle + pi
        while angle >= 2 * pi:
            angle -= 2 * pi
        return angle
        
            
    """
    This next function attempts to 'add' a new angle in. What it does 
    is checks to see whether the vector is within the inclusion bounds.
    If so it returns True. It then checks to see if it is in the 
    exclusion bounds, if so it returns False. Finally, if neither of these
    are the case, it sets the new one as a new bound and returns True.
    
    Note, it also looks to see if an orientation selection is needed, 
    and tries to do it.
    
    Essentially this contains the checks for each new column of our matrix
    C (for a particular angle that is of course)
    """
    def AddAngle(self, angle):
        # first we check to see if an orientation 
        if self.WAITING_FOR_ORIENTATION:
            """
            Here we take the first angle in self.angles are see if the 
            clockwise or counterclockwise rotate to the new angle is better. If 
            neither is we just return True (we are still in the same boat)
            Then if the clockwise is the best we set the 'upper' to the angle
            we picked and 'lower' to the other angle and follow the same procedure
            as for SetBounds. We do the opposite for counter-clockwise. 
            Then we set self.WAITING_FOR_ORIENTATION to False and return True
            """
            clockwise = self.rotateTo(self.angles[0], angle)
            counter_clockwise = self.rotateTo(self.angles[0], angle)
            if clockwise == counter_clockwise:
                return True
            elif clockwise < counter_clockwise:
                self.lower = self.angles[1]
                self.upper = self.angles[0]
                if self.upper < self.lower:
                    self.inclusion_bounds.append((self.lower, 2*pi))
                    self.inclusion_bounds.append((0,self.upper))
                else:
                    self.inclusion_bounds.append(self.lower, self.upper)
            elif counter_clockwise < clockwise:
                self.lower = self.angles[0]
                self.upper = self.angles[1]
                if self.upper < self.lower:
                    self.inclusion_bounds.append((self.lower, 2*pi))
                    self.inclusion_bounds.append((0,self.upper))
                else:
                    self.inclusion_bounds.append(self.lower, self.upper)
            self.WAITING_FOR_ORIENTATION = False
            return True
        # now we handle adding an angle and checking exclusion area
        # we check the exclusion area
        for bound in self.exclusion_bounds:
            if angle < bound[0] and angle > bound[1]:
                return False
        for bound in self.inclusion_bounds:
            if angle < bound[0] and angle > bound[1]:
                return True
        # finally it must be outside of both bounds, so we need to 
        # re-adjust the inclusion and exclusion bounds
        if angle < self.lower:
            # now we have to check that it is not both larger than the 
            # upper bound and less than the lower bound 
            if not angle > self.upper:
                self.inclusion_bounds = self.getSliceBounds(self.upper, angle)
                self.exclusion_bounds = self.getSliceBounds(self.getOppositeAngle(self.upper), self.getOppositeAngle(angle))
            else:
                # in this case we have to which it is closer to and have it replace
                # that one. Note it cannot be the same distance, because that 
                # would put it in the exclusion zone
                if angle - self.upper < self.lower - angle:
                    self.inclusion_bounds = self.getSliceBounds(self.lower, angle)
                    self.exclusion_bounds = self.getSliceBounds(self.getOppositeAngle(self.lower), self.getOppositeAngle(angle))
                else:
                    self.inclusion_bounds = self.getSliceBounds(self.upper, angle)
                    self.exclusion_bounds = self.getSliceBounds(self.getOppositeAngle(self.upper), self.getOppositeAngle(angle))
        else:
            self.inclusion_bounds = self.getSliceBounds(self.lower, angle)
            self.exclusion_bounds = self.getSliceBounds(self.getOppositeAngle(self.lower), self.getOppositeAngle(angle))           
        return True  