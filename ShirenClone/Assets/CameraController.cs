using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class CameraController : MonoBehaviour {

    public float speed = 1.0f;

    public Vector4 range;
    public float floorHeight = 1;
    public bool isUpdateCornerObject = true;

    public Camera camera;

    // debug objects marking corners of the camera view
    private GameObject[] corners = null;
    public GameObject[] cornerPrefab;

    private void Awake()
    {
        camera = GetComponent<Camera>();
    }

    // Use this for initialization
    void Start () {
        initMapCornerTests();

        initRange(camera, floorHeight, out range);
        updateCornerObjects();
    }
	
	// Update is called once per frame
	void Update () {
        float horizontal = Input.GetAxis("Horizontal");
        float vertical = Input.GetAxis("Vertical");
        // why value of y will change?
        transform.Translate(new Vector3(horizontal, 0, vertical) * speed * Time.deltaTime, Space.World);

        initRange(camera, floorHeight, out range);
        updateCornerObjects();
    }

    void initRange(Camera camera, float floorHeight, out Vector4 range)
    {
        float vfov = camera.fieldOfView / 2.0f;
        float vfovRad = vfov * Mathf.Deg2Rad;
        Vector3 eulerAngles = camera.transform.rotation.eulerAngles;
        float h = camera.transform.position.y - floorHeight;
        float zfar = h * xdist(eulerAngles.x - vfov);
        float znear = h * xdist(eulerAngles.x + vfov);
        range.x = -Mathf.Sqrt(Mathf.Pow(zfar, 2f) + Mathf.Pow(h, 2f)) * camera.aspect * Mathf.Sin(vfovRad);
        range.y = -range.x;
        range.z = znear;
        range.w = zfar;
    }

    float xdist(float theta)
    {
        if (theta <= 0f || theta >= 180f)
        {
            throw new System.ArgumentOutOfRangeException("theta", theta, "theta should be within (0f, 180f)");
        }

        float theta_rad = theta * Mathf.Deg2Rad;
        if (theta <= 90f)
        {
            return 1.0f / Mathf.Tan(theta_rad);
        } else
        {
            return -Mathf.Tan(theta_rad - Mathf.PI / 2.0f);
        }
    }

    void initMapCornerTests()
    {
        if (corners == null)
        {
            corners = new GameObject[4];
        }
        corners[0] = Instantiate(cornerPrefab[0], new Vector3(), Quaternion.identity) as GameObject;
        //corners[1] = Instantiate(cornerPrefab[1], new Vector3(), Quaternion.identity) as GameObject;
        corners[2] = Instantiate(cornerPrefab[0], new Vector3(), Quaternion.identity) as GameObject;
        //corners[3] = Instantiate(cornerPrefab[1], new Vector3(), Quaternion.identity) as GameObject;
    }

    void updateCornerObjects()
    {
        if (isUpdateCornerObject)
        {
            corners[0].transform.position = new Vector3(camera.transform.position.x, floorHeight, camera.transform.position.z + range.z);
            corners[2].transform.position = new Vector3(camera.transform.position.x + range.x, floorHeight, camera.transform.position.z + range.w);
        }
    }
}
