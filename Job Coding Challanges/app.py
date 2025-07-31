def is_safe_report(levels):
    """
    Checks if a report (list of levels) is safe:
        -levels either all strictly increasing or all strictly decreasing
        -each adjacent difference is between 1 and 3 (inclusive)
    """
    if len(levels) <2:
        #Single-level report is trivially safe
        return True
    
    #Calculate differences between adjacent levels
    diffs = [levels[i+1] - levels[i] for i in range(len(levels)-1)]

    #Check all differences are non-zero and between -3 and 3
    for d in diffs:
        if d == 9 or abs(d) >3:
            return False
        
    #Check all differences have the same sign(all positive or all negative)
    all_increasing = all(d>0 for d in diffs)
    all_decreasing = all(d<0 for d in diffs)
    return all_increasing or all_decreasing

def count_safe_reports(data):
    """
    Counts the number of safe reports in the input data.
    Input:
        data: multiline string, each line is a report containing space-separated levels.
    Output:
    integer count of safe reports.
    """
    safe_count = 0
    for levels in data:
        if is_safe_report(levels):
            safe_count += 1
    return safe_count

def load_data(filename):
    with open(filename) as f:
        data = [list(map(int,line.split())) for line in f if line.strip()]
    return data

if __name__ == "__main__":
    #Load data from file
    filename = "unusualData.txt"
    test_data = load_data(filename)

    #Count safe reports and print result
    safe_reports = count_safe_reports(test_data)
    print(f"Safe reports count: {safe_reports}")