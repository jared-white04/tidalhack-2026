import math
import numpy as np

def calculate_confidence_score(jlen_arr, logdist_arr, elevation_arr, rotation_arr, depth, bool_arr):
    a_score = 0.4*allignment_score(jlen_arr, logdist_arr, elevation_arr, rotation_arr)
    p_score = 0.4*persistence_score(bool_arr)
    m_score = 0.2*magnitude_score(depth)
    
    return a_score + p_score + m_score  # Example confidence score

def allignment_score(jlen_arr, logdist_arr, elevation_arr, rotation_arr):
    j = [d for d in jlen_arr if d is not None and d > 0]
    l = [d for d in logdist_arr if d is not None and d > 0]
    e = [d for d in elevation_arr if d is not None and d > 0]
    r = [d for d in rotation_arr if d is not None and d > 0]
    
    j_mean = np.mean(j)
    j_stdev = np.std(j)
    l_mean = np.mean(l)
    l_stdev = np.std(l)
    e_mean = np.mean(e)
    e_stdev = np.std(e)
    r_mean = np.mean(r)
    r_stdev = np.std(r)
    
    j_cv = j_stdev / j_mean if j_mean != 0 else 0
    l_cv = l_stdev / l_mean if l_mean != 0 else 0
    e_cv = e_stdev / e_mean if e_mean != 0 else 0
    r_cv = r_stdev / r_mean if r_mean != 0 else 0
    score = 1 - (j_cv + l_cv + e_cv + r_cv) / 4  # Average CV and invert for score
    
    print(score)
    return score

def persistence_score(bool_arr):
    count = 0
    for i in bool_arr:
        if i:
            count += 1
    print(count/len(bool_arr))
    return count / len(bool_arr) 

def magnitude_score(depth):
    threshold = 0.8
    if depth <= 0:
        return 0.0
    
    print(min(1.0, depth / threshold))
    return min(1.0, depth / threshold)

def calculate_growth_rate(d0,df,l0,lf,w0,wf,time):
    V0 = d0 * l0 * w0 
    Vf = df * lf * wf
    growth_rate = (Vf - V0) / time 
    
    return growth_rate  # Return the calculated growth rate

def calculate_severity_score(rpr_scores, years):
    # takes in array of rpr scores from each year
    decay_rate_sum = 0
    for i in range(0,len(rpr_scores)-1):
        decay_rate = (rpr_scores[i+1] - rpr_scores[i]) / (years[i+1] - years[i])
        decay_rate_sum += decay_rate
    decay_rate_sum /= -1 * (len(rpr_scores) - 1)  # Average decay rate

    years_until_implode = (rpr_scores[-1] - 1) / decay_rate_sum if decay_rate_sum != 0 else float('inf')  # Avoid division by zero
    severity_score = 1 / (1 + math.exp(-decay_rate_sum))  # Sigmoid function to scale severity score between 0 and 1
    
    return severity_score 

def main():
    # rpr_scores = [float(x) for x in input("Enter RPR scores separated by spaces: ").split()]
    # years = [float(x) for x in input("Enter corresponding years separated by spaces: ").split()]
    # print(calculate_severity_score(rpr_scores, years))
    
    jlen_arr = [1.0, 1.2, 0.8, 1.1]
    logdist_arr = [0.5, 0.6, 0.4, 0.7]
    elevation_arr = [0.2, 0.3, 0.1, 0.4]
    rotation_arr = [0.05, 0.06, 0.04, 0.07]
    depth = 0.5
    bool_arr = [True, True, False, True]
    confidence_score = calculate_confidence_score(jlen_arr, logdist_arr, elevation_arr, rotation_arr, depth, bool_arr)
    print(f"Confidence Score: {confidence_score}")
    
    
    
if __name__ == "__main__":    
    main()