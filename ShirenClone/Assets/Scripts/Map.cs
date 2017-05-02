using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Map : MonoBehaviour {

    public enum grid_type {
        GRID_INVALID = -1,
        GRID_EMPTY = 0,
        GRID_BLOCK = 1,
        GRID_MAX = 2
    };

    public int width = 10;
    public int height = 10;

    // -1 invalid
    // 0  empty
    // 1  block
    private grid_type[] grids;

    public grid_type GetGrid(int x, int y) {
        int index = y * height + x;
        if (index < 0 || index >= width * height)
        {
            return grid_type.GRID_INVALID;
        }
        return grids[y * height + x];
    }

    private void initGrids()
    {
        int size = width * height;
        grids = new grid_type[size];
        for (int i = 0; i < size; ++ i)
        {
            grids[i] = (grid_type)Random.Range(0, (int)grid_type.GRID_MAX);
        }
    }

    private void Awake()
    {
        initGrids();
    }

    // Use this for initialization
    void Start () {
		
	}
	
	// Update is called once per frame
	void Update () {
		
	}
}
