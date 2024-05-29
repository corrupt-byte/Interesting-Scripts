using UnityEngine;
using UnityEditor;
using System;
using System.Reflection;
using System.Collections.Generic;
using System.IO;

public class AssetPropertyReporter : EditorWindow
{
    [MenuItem("Tools/Generate Asset Property Report")]
    public static void ShowWindow()
    {
        GetWindow<AssetPropertyReporter>("Asset Property Reporter");
    }

    private void OnGUI()
    {
        if (GUILayout.Button("Generate Report"))
        {
            GenerateReport();
        }
    }

    private static void GenerateReport()
    {
        var allTypes = Assembly.GetAssembly(typeof(UnityEngine.Object)).GetTypes();
        var assetTypes = new List<Type>();

        foreach (var type in allTypes)
        {
            if (type.IsSubclassOf(typeof(UnityEngine.Object)) && !type.IsAbstract)
            {
                assetTypes.Add(type);
            }
        }

        var report = new List<AssetPropertyInfo>();

        foreach (var type in assetTypes)
        {
            var properties = type.GetProperties(BindingFlags.Public | BindingFlags.Instance);
            var fields = type.GetFields(BindingFlags.Public | BindingFlags.Instance);
            var propertyInfos = new List<PropertyInfo>();

            foreach (var property in properties)
            {
                propertyInfos.Add(new PropertyInfo
                {
                    Name = property.Name,
                    Type = property.PropertyType.Name
                });
            }

            foreach (var field in fields)
            {
                propertyInfos.Add(new PropertyInfo
                {
                    Name = field.Name,
                    Type = field.FieldType.Name
                });
            }

            report.Add(new AssetPropertyInfo
            {
                AssetType = type.Name,
                Properties = propertyInfos
            });
        }

        SaveReport(report);
    }

    private static void SaveReport(List<AssetPropertyInfo> report)
    {
        var path = EditorUtility.SaveFilePanel("Save Report", "", "AssetPropertyReport.json", "json");
        if (string.IsNullOrEmpty(path)) return;

        var json = JsonUtility.ToJson(new ReportWrapper { Assets = report }, true);
        File.WriteAllText(path, json);
        EditorUtility.DisplayDialog("Report Generated", "The report has been generated successfully.", "OK");
    }

    [Serializable]
    public class AssetPropertyInfo
    {
        public string AssetType;
        public List<PropertyInfo> Properties;
    }

    [Serializable]
    public class PropertyInfo
    {
        public string Name;
        public string Type;
    }

    [Serializable]
    public class ReportWrapper
    {
        public List<AssetPropertyInfo> Assets;
    }
}
