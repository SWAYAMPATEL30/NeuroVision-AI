import h5py
import json

def upgrade_to_keras3_nodes(filepath):
    print(f"Upgrading {filepath} to Keras 3 nodes...")
    with h5py.File(filepath, "r+") as f:
        model_config_str = f.attrs.get("model_config")
        if not model_config_str: return
        if isinstance(model_config_str, bytes): model_config_str = model_config_str.decode("utf-8")
        
        config = json.loads(model_config_str)
        layers = config.get("config", {}).get("layers", [])
        
        for layer in layers:
            inbound = layer.get("inbound_nodes", [])
            if not isinstance(inbound, list): continue
            
            new_nodes = []
            for node in inbound:
                # If it's the old style [name, idx, shard, kwargs]
                if isinstance(node, list) and len(node) >= 4 and isinstance(node[0], str):
                    name, idx, shard, kwargs = node[0], node[1], node[2], node[3]
                    # Upgrading to Keras 3 dictionary format
                    new_nodes.append({
                        "args": [{
                            "class_name": "__keras_tensor__",
                            "config": {
                                "keras_history": [name, idx, shard]
                                # Shape/Dtype are often filled automatically by Keras 3 or can be null
                            }
                        }],
                        "kwargs": kwargs
                    })
                else:
                    new_nodes.append(node)
            layer["inbound_nodes"] = new_nodes
            
        f.attrs["model_config"] = json.dumps(config).encode("utf-8")
        print(f"File upgraded: {filepath}")

if __name__ == "__main__":
    upgrade_to_keras3_nodes("major_project-main/models/resnet_model.h5")
    upgrade_to_keras3_nodes("major_project-main/models/inception_model.h5")
