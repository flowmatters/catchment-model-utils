import pandas as pd

def _find_starting_points(connectivity):
    conn = connectivity.transpose()
    return list(conn[(conn.sum()==0)].index)

def _compute_dr(site,ds_sites,result,connectivity,local_inputs,outputs,outlet):
    upstream_sites = list(connectivity[connectivity[site]>0].index)
    non_local_inputs = sum([outputs[s] for s in upstream_sites],0.0)
    dr = outputs[site]/(local_inputs[site]+non_local_inputs)
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