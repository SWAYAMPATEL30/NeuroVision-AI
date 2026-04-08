import h5py
import json

def fix_model_h5(filepath):
    print(f"Fixing {filepath}...")
    with h5py.File(filepath, "r+") as f:
        model_config_str = f.attrs.get("model_config")
        if model_config_str is None:
            print("No model_config found.")
            return

        if isinstance(model_config_str, bytes):
            model_config_str = model_config_str.decode("utf-8")
        
        config = json.loads(model_config_str)

        # Standard Functional/Sequential structure
        layers = config.get("config", {}).get("layers", [])
        
        def fix_nodes(nodes):
            if not isinstance(nodes, list):
                return nodes
            
            new_nodes = []
            for node in nodes:
                # Keras 2.13+ format: [{'args': [{'class_name': '__keras_tensor__', 'config': {'keras_history': [layer_name, node_idx, tensor_idx]}}], 'kwargs': {}}]
                if isinstance(node, dict) and 'args' in node:
                    args = node['args']
                    # Flatten it back to [layer_name, node_idx, tensor_idx, kwargs]
                    if isinstance(args, list) and len(args) > 0:
                        kt = args[0]
                        if isinstance(kt, dict) and kt.get('class_name') == '__keras_tensor__':
                            hist = kt.get('config', {}).get('keras_history', [])
                            if len(hist) >= 3:
                                # New format is [name, i, j, {kwargs}]
                                new_nodes.append([hist[0], hist[1], hist[2], node.get('kwargs', {})])
                                continue
                
                # If it's already a list or other format we don't know, keep it
                new_nodes.append(node)
            return new_nodes

        for layer in layers:
            if "inbound_nodes" in layer:
                layer["inbound_nodes"] = fix_nodes(layer["inbound_nodes"])
        
        # Also fix output_layers if needed (usually just names)
        # config['config']['output_layers']
        
        f.attrs["model_config"] = json.dumps(config).encode("utf-8")
        print(f"File fixed: {filepath}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        fix_model_h5(sys.argv[1])
    else:
        fix_model_h5("major_project-main/models/resnet_model.h5")
        fix_model_h5("major_project-main/models/inception_model.h5")
