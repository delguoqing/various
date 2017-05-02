using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class MapView : MonoBehaviour {

    public Map map_data = null;
    public GameObject[] prototypes = null;

	// Use this for initialization
	void Start () {
        //initMapImmediate();
	}
	
    void initMapImmediate()
    {
        for (int i = 0; i < map_data.width; ++i)
        {
            for (int j = 0; j < map_data.height; ++j)
            {
                Map.grid_type grid_type = map_data.GetGrid(i, j);
                Instantiate(prototypes[(int)grid_type], new Vector3(i * 4f, 0f, j * 4f), Quaternion.identity);
            }
        }
    }

	// Update is called once per frame
	void Update () {
		
	}
}
