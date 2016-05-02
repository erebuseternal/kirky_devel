from math import pi, atan2, sin, cos
from pyx import path
from issue import Issue
from vertex import Index
from copy import copy
from fractions import Fraction

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
This first class handles exclusion and inclusion once we have chosen a 
plane 
"""


class Angle:
    
    def __init__(self, value):
        self.value = self.canonicalize(value)
    
    # canonicalization places the angle in the range [0, 2pi)
    def canonicalize(self, value):
        while value < 0:
            value += 2.0 * pi
        while value >= 2 * pi:
            value -= 2.0 * pi
    
    # this returns the number of radians needed to rotate the current 
    # angle to the other angle in a counterclockwise direction      
    def rotation(self, other):
        if self.value == other.value:
            return Angle(0.0)
        # if the other is larger than self, its easy we just take the 
        # difference
        if self.value < other.value:
            return other - self
        # otherwise in moving counterclockwise we will move through 
        # 0, therefore we have to take advantage of this
        if other.value < self.value:
            return (Angle(2.0 * pi) - self) + other
        
    def opposite(self):
        return Angle(self.value + pi)
    
    # this is exactly what you'd think   
    def __eq__(self, other):
        if self.value == other.value:
            return True
        else:
            return False
        
    # self is greater than other if the counterclockwise rotation from
    # other to self is less than the other way around or if both 
    # rotations are equal but self - other is greater than 0. Note
    # that this means that 0 < pi but also 2 pi < pi (because how 
    # we have decided to standardize
    def __gt__(self, other):
        self_other = self.rotation(other)
        other_self = other.rotation(self)
        if other_self.value < self_other.value:
            return True
        elif other_self.value == self_other.value and self.value - other.value > 0:
            return True
        else:
            return False
        
    # we define this based off of __gt__ and __eq__
    def __lt__(self, other):
        if not self > other and not self == other:
            return True
        else:
            return False
        
    def __ge__(self, other):
        if self > other or self == other:
            return True
        else:
            return False
        
    def __le__(self, other):
        if not self > other:
            return True
        else:
            return False
        
    def __add__(self, other):
        return Angle(self.value + self.other)
    
    def __mul__(self, scalar):
        return Angle(self.value * scalar)

    def __sub__(self, other):
        return Angle(self.value - other.value)
        
    def __str__(self):
        return str(self.value)
    
    def __repr__(self):
        return str(self)
    
    def __hash__(self):
        return hash(self.value)

class Slice:
    
    def __init__(self, angle1, angle2, IS_EXCLUSION_SLICE=False):
        self.Setup(angle1, angle2, IS_EXCLUSION_SLICE)
            
    def Setup(self, angle1, angle2, IS_EXCLUSION_SLICE=False):
        self.WAITING_FOR_ORIENTATION = False
        self.lower = None
        self.upper = None
        # we classify the angles 
        self.ClassifyAngles(angle1, angle2)
        # now we set the two bounds
        if not self.WAITING_FOR_ORIENTATION:
            self.SetBounds()
        self.pi = Angle(pi)
        self.IS_EXCLUSION_SLICE = IS_EXCLUSION_SLICE
        self.exclusion_slice = None
        # now we check to see if we need to make an exclusion slice
        if not self.WAITING_FOR_ORIENTATION and not self.IS_EXCLUSION_SLICE:
            self.SetExclusionSlice()
            
    def __contains__(self, angle):
        if self.IS_EXCLUSION_SLICE:
            # exclusion slices are open intervals
            for bound in self.bounds:
                if angle < bound[1] and angle > bound[0]:
                    return True
        else:
            for bound in self.bounds:
                if angle <= bound[1] and angle >= bound[0]:
                    return True
        return False
      
    def ClassifyAngles(self, angle1, angle2):
        # first we set the larger of the two to upper and the smaller
        # to lower
        if angle1 >= angle2:
            self.upper = angle1
            self.lower = angle2
        else:
            self.upper = angle2
            self.lower = angle1
        # next we look to make sure that these two are not separated by 
        # pi, in which case we will have to wait for a third angle to 
        # determine the orientation of the slice
        if self.upper - self.lower == Angle(pi):
            self.WAITING_FOR_ORIENTATION = True
            return
        
    def SetBounds(self):
        # Note that we have to deal with 
        # the case where the bound includes 2pi. This is what this
        # first condition does
        if self.upper.value < self.lower.value:
            self.bounds.append((self.lower, 2.0 * self.pi))
            self.bounds.append((0.0,self.upper))
        else:
            self.bounds.append((self.lower, self.upper))
    
    def SetExclusionSlice(self):
        # first we can only set exclusion slices on 
        # slices that aren't exclusion slices
        if self.IS_EXCLUSION_SLICE:
            raise Issue('cannot add exclusion slice to exclusion slice')
        # this is the slice composed of two angles:
        # the angle pi/2 greater than upper angle or opposite to
        # the the lesser angle, whichever is smaller. And the angle
        # pi/2 smaller than the lower angle or opposite the upper 
        # angle, in this case whichever is larger.
        # So first we get these angles. 
        increment = self.upper + (1/2) * self.pi
        opposite = self.lower.opposite()
        if increment <= opposite:
            angle1 = increment
        else:
            angle1 = opposite
        increment = self.lower - (1/2) * self.pi
        opposite = self.upper.opposite()
        if increment >= opposite:
            angle2 = increment
        else:
            angle2 = opposite
        # now we can set the exclusion slice
        self.exclusion_slice = Slice(angle1, angle2, False)
        
            
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
            # our orientation is now determined in the following way.
            # Whichever angle (upper or lower) that is larger than 
            # angle becomes the upper. If the angle is equal to either 
            # angle we just pass on. In either case we return True
            if angle == self.upper or angle == self.lower:
                return True
            if self.lower > angle:
                self.upper, self.lower = (self.lower, self.upper)
            # note we don't care about the case when self.upper > angle
            # anyways now we can set our bounds
            self.SetBounds()
            # finally, now we unset WAITING_FOR_ORIENTATION, and if this 
            # is not an exclusion slice, we need to set the exclusion 
            # slice now
            self.WAITING_FOR_ORIENTATION = False
            if not self.IS_EXCLUSION_SLICE:
                self.SetExclusionSlice()
            # and we are done here!
            return True
        # in this case our slice and its exclusion bound is well set
        # so we can now go ahead and attempt to add our angle as per
        # le norm
        # first we check the exclusion area
        if angle in self.exclusion_slice:
            return False
        # next we check the bounds on this slice
        if angle in self:
            return True
        # finally if it is in neither, then this new angle is going 
        # to extend our bounds! so we need to see in which direction it 
        # does so. To do this, we need to see if it smaller than the lower
        # bound, or larger that the upper bound. Because we already 
        # checked the exclusion area, there can be no other option
        if angle > self.upper:
            lower = self.lower
            # so we start by classifying our angles and setting our bounds 
            self.Setup(angle, self.upper)
            # now we need to check to see if our slice is waiting for 
            # its orientation, in which case we fix the orientation with 
            # lower
            if self.WAITING_FOR_ORIENTATION:
                self.AddAngle(lower)
            # and we are done!
            return True
        if angle < self.lower:
            upper = self.upper
            self.Setup(angle, self.lower)
            if self.WAITING_FOR_ORIENTATION:
                self.AddAngle(upper)
            return True

    def Draw(self, canvas, circle_size):
        if not self.IS_EXCLUSION_SLICE:
            self.exclusion_slice.DrawBounds(canvas, circle_size)
        self.Draw(canvas, circle_size)

    def DrawBounds(self, canvas, circle_size):
        # so we are going to essentially draw two lines within the 
        # square given by the bounds (x,y)
        # we start with the upper
        canvas.stroke(path.line(0,0,circle_size * cos(self.upper.value[0]), circle_size * sin(self.upper.value[0])))
        # then we do the lower
        canvas.stroke(path.line(0,0,circle_size * cos(self.lower.value[0]), circle_size * sin(self.lower.value[0])))

class Point:

    def __init__(self, position):
        self.position = position

class InteriorPointFinder:

    def __init__(self, slice):
        self.points = []
        self.interior = []
        self.used_positions = []
        self.index = Index(2, 0, 2)
        self.slice = slice

    def GrowAbout(self, position):
        # this method adds lattice points in a square around the position
        for i in range(-1, 2):
            for j in range(-1, 2):
                new_position = copy(position)
                new_position[0] += i
                new_position[1] += j
                if not self.index.GetElement(new_position):
                    point = Point(new_position)
                    self.index.AddElement(point)
                    self.points.append(point)

    def FindBestPoint(self):
        # this finds the point closest to the slice interior that hasn't already
        # been used
        current_best_distance = 10000000
        best_point = None
        # we run through the points
        for point in self.points:
            # we skip points that have already been used
            if point.position in self.used_positions:
                continue
            angle = self.GetAngle(point)
            # we get the angle differences (as positive numbers)
            upper_dif = abs(angle.value - self.slice.upper.value)
            lower_dif = abs(angle.value - self.slice.lower.value)
            # and now we just find the smallest one and compare it the current_best_distance
            if upper_dif >= lower_dif:
                if lower_dif < current_best_distance:
                    current_best_distance = lower_dif
                    best_point = point
            else:
                if upper_dif < current_best_distance:
                    current_best_distance = upper_dif
                    best_point = point
        return best_point

    def FindInteriorPoints(self):
        for point in self.points:
            angle = self.GetAngle(point)
            if angle in self.slice:
                self.interior.append(point)

    def GetAngle(self, point):
        angle_value = atan2(point.position[1], point.position[0])
        angle = Angle(angle_value)
        return angle

    # this method grows our lattice until we find one or more interior points
    # it returns the first one in the list of discovered ones
    def FindInteriorPoints(self, max=None):
        # first we grow about 0,0
        self.GrowAbout([0,0])
        # then we look to see if there are any points inside the slice
        self.FindInteriorPoints()
        # this just tracks how many iterations we have done so far
        count = 0
        while not self.interior:
            # so while we haven't found anything inside the slice
            # we find the closest point
            point = self.FindBestPoint()
            # then we grow about that point
            self.GrowAbout(point.position)
            # we mark it off as having been used
            self.used_positions.append(point.position)
            # and we look for interior points
            self.FindInteriorPoints()
            count += 1
            # this checks to see if we have maxed out on iterations
            if max and count == max:
                break
        return self.interior[0]

    def Draw(self, canvas):
        for point in self.points:
            canvas.fill(path.circle(point.position[0], point.position[1], 0.04))

# this just ties together the previous classes really nicely
class Splitter:

    def __init__(self, angle1, angle2):
        self.slice = Slice(angle1, angle2)
        self.point_finder = InteriorPointFinder(self.slice)

    def TryAngle(self, angle):
        return self.slice.AddAngle(angle)

    def FindPoint(self):
        return self.point_finder.FindInteriorPoints()

"""
The following class takes a matrix and finds the size of the space you 
are working in and then divides things up into planes, grabs angles for 
each column vector and then works its way through the columns trying 
to find the appropriate angles if it can find them
""" 

class RowPositive:
    
    def __init__(self, C):
        self.matrix = C
        self.dimension = self.matrix.shape[0]   # the number of rows is our dimension
        # we will choose the first entry in column as the default 
        # for what each other dimension will create a plane with
        self.splitters = []    # this will contain, in order of planes, the splitters corresponding
                            # to them.

    # this checks to make sure all of the columns are splittable and generates the splitters
    # as you go
    def CheckAndGenerate(self):
        # first we grab two columns and generate the slices 
        # for each of the planes
        column1 = self.matrix[:,0]
        column2 = self.matrix[:,1]
        for dimension in range(1, self.dimension):
            angle1 = self.GetAngle(column1, dimension)
            angle2 = self.GetAngle(column2, dimension)
            splitter = Splitter(angle1, angle2)
            self.splitters.append(splitter)
        # now we run through the rest of the columns and try
        # to add in their vectors. If anyone fails we return False
        # otherwise we return True
        for i in range(2, self.matrix.shape[1]):
            column = self.matrix[:,i]
            for dimension in range(1, self.dimension):
                angle = self.GetAngle(column, dimension)
                if not self.splitters[dimension].TryAngle(angle):
                    return False
        return True

    def GetV(self):
        # this goes through the splitters and gets the points that fall within each splitter's slice
        # then it scales all of them so that each points first entry (that corresponding to the zeroth
        # dimension) is the same. Then it creates an array out of these and returns that
        points = []
        for splitter in self.splitters:
            points.append(splitter.FindPoint())
        # now we scale the tuples
        scaled_points = ScaleTuples(points)
        # and now we create our new vector
        vector = [scaled_points[0][0]]
        for point in scaled_points:
            vector.append(point[1])
        return vector

    def GetAngle(self, vector, dimension):
        y = vector[0]
        x = vector[dimension]
        value = atan2(y,x)
        return Angle(value)

def ScaleTuples(tuples):
    fracs = []
    for tup in tuples:
        fracs.append(Fraction(tup[1], tup[0]))
    sum = Fraction()
    for frac in fracs:
        sum += frac
    denominator = sum.denominator
    new_tuples = []
    for tup in tuples:
        scaling = denominator / Fraction(tup[0])
        new_tup = (denominator, scaling * Fraction(tup[1]))
        new_tuples.append(new_tup)
    return new_tuples



        