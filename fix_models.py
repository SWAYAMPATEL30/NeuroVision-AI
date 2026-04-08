import h5py
import json
import glob

def fix_h5_compatibility(filepath):
    try:
        with h5py.File(filepath, 'r+') as f:
            if 'model_config' in f.attrs:
                model_config_str = f.attrs['model_config']
                
                if isinstance(model_config_str, bytes):
                    model_config_str = model_config_str.decode('utf-8')
                    
                model_config = json.loads(model_config_str)
                
                modified = False
                def fix_dict(d):
                    nonlocal modified
                    if isinstance(d, dict):
                        # Fix batch_shape
                        if 'batch_shape' in d:
                            d['batch_input_shape'] = d.pop('batch_shape')
                            modified = True
                            
                        # Fix DTypePolicy error by converting DTypePolicy dictionary back to string dtype
                        if 'dtype' in d and isinstance(d['dtype'], dict):
                            if d['dtype'].get('class_name') == 'DTypePolicy':
                                d['dtype'] = d['dtype']['config']['name']
                                modified = True
                        
                        # Recursively fix nested
                        for k, v in d.items():
                            fix_dict(v)
                    elif isinstance(d, list):
                        for item in d:
                            fix_dict(item)
                            
                fix_dict(model_config)
                
                if modified:
                    f.attrs['model_config'] = json.dumps(model_config).encode('utf-8')
                    print(f"Fixed compatibility issues in {filepath}")
                else:
                    print(f"No compatibility issues found in {filepath}")
            else:
                print(f"No model_config found in {filepath}")
    except Exception as e:
        print(f"Error processing {filepath}: {e}")

# Process all model files
for file in glob.glob("major_project-main/models/*.h5"):
    fix_h5_compatibility(file)
