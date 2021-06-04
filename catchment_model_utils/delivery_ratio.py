from collections import defaultdict
import pandas as pd

DR_TOLERANCE=1e-2

def _find_starting_points(connectivity):
    conn = connectivity.transpose()
    return list(conn[(conn.sum()==0)].index)

def _compute_dr(site,ds_sites,result,connectivity,local_inputs,outputs,outlet):
    local_inputs = defaultdict(float,(local_inputs or {}).items())
    outputs = defaultdict(float,(outputs or {}).items())
    upstream_sites = list(connectivity[connectivity[site]>0].index)
    non_local_inputs = sum([outputs[s] for s in upstream_sites],0.0)
    total_output = outputs[site]
    if total_output == 0.0:
        dr = 0.0
    else:
        total_input = (local_inputs[site]+non_local_inputs)
        if total_input==0.0:
            print(f'At {site}, output is {total_output}, but total_input is 0.0')
        dr = total_output/total_input
        # if (dr > 1) and (dr < (1+DR_TOLERANCE)):
        #     dr = 1
        # if dr > 1:
        #     print(f'At {site}, output is {total_output}, but total_input is {total_input}, yield a ratio of {dr}')
        #     print(f'local:{local_inputs[site]},non_local:{non_local_inputs}')
        #     print(f'upstream sites: {upstream_sites}')
        #     # assert False
    result.loc[site,site]=dr
    for (ds_site,existing_dr) in ds_sites:
        result.loc[site,ds_site] = existing_dr * dr
    result.loc[site,'outlet']=result.loc[site,outlet]
    for s in upstream_sites:
        ds_sites = [(site,dr)]+ds_sites
        _compute_dr(s,ds_sites,result,connectivity,local_inputs,outputs,outlet)

def delivery_ratio_table(connectivity,local_inputs,outputs):
    '''
    Compute a table of delivery ratios based on the model topology represented by connectivity, and a set of local_inputs and outputs

    Returns: DataFrame of contributing locations (rows) and the fraction of their local inputs that are represented in the output
    of each other location (column), as well as the eventual outlet ('outlet' column)
    '''
    result = pd.DataFrame(index=connectivity.columns,columns=list(connectivity.columns)+['outlet'],dtype='f').fillna(0.0)
    
    starting_sites = _find_starting_points(connectivity)
    for site in starting_sites:
        _compute_dr(site,[],result,connectivity,local_inputs,outputs,site)
    return result