using UnityEngine;
using UnityEditor;
using System;
using System.Reflection;
using System.Collections.Generic;
using System.IO;
using System.Linq;

public class CustomAssetPropertyReporter : EditorWindow
{
    private const int MaxDepth = 10; // Safeguard to prevent too deep recursion

    [MenuItem("Tools/Generate Custom Asset Property Report")]
    public static void ShowWindow()
    {
        GetWindow<CustomAssetPropertyReporter>("Custom Asset Property Reporter");
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
        var allTypes = AppDomain.CurrentDomain.GetAssemblies()
            .SelectMany(assembly => assembly.GetTypes())
            .Where(type => type.IsSubclassOf(typeof(ScriptableObject)) && !type.IsAbstract)
            .ToList();

        var report = new List<AssetPropertyInfo>();

        foreach (var type in allTypes)
        {
            var propertyInfos = new List<PropertyInfoWrapper>();
            ProcessType(type, propertyInfos, "", 0);

            report.Add(new AssetPropertyInfo
            {
                AssetType = type.Name,
                Properties = propertyInfos
            });
        }

        SaveReport(report);
    }

    private static void ProcessType(Type type, List<PropertyInfoWrapper> propertyInfos, string parentPath, int depth)
    {
        if (depth > MaxDepth) return; // Safeguard check

        var properties = type.GetProperties(BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance);

        foreach (var property in properties)
        {
            if (property.GetIndexParameters().Length == 0) // Ignore indexers
            {
                var fullPath = string.IsNullOrEmpty(parentPath) ? property.Name : $"{parentPath}.{property.Name}";
                var propertyInfo = new PropertyInfoWrapper
                {
                    Name = fullPath,
                    Type = property.PropertyType.Name,
                    Description = GetPropertyDescription(property),
                    Group = GetPropertyGroup(property),
                    Children = new List<PropertyInfoWrapper>() // Initialize the Children list
                };

                if (!IsPrimitiveType(property.PropertyType))
                {
                    ProcessType(property.PropertyType, propertyInfo.Children, fullPath, depth + 1);
                }

                propertyInfos.Add(propertyInfo);
            }
        }
    }

    private static bool IsPrimitiveType(Type type)
    {
        return type.IsPrimitive || type == typeof(string) || type == typeof(decimal) || type.IsEnum || type == typeof(DateTime);
    }

    private static string GetPropertyDescription(System.Reflection.PropertyInfo property)
    {
        var tooltipAttributes = property.GetCustomAttributes(typeof(TooltipAttribute), true).Cast<TooltipAttribute>().ToArray();
        return tooltipAttributes.Length > 0 ? string.Join(", ", tooltipAttributes.Select(attr => attr.tooltip)) : "";
    }

    private static string GetPropertyGroup(System.Reflection.PropertyInfo property)
    {
        var headerAttributes = property.GetCustomAttributes(typeof(HeaderAttribute), true).Cast<HeaderAttribute>().ToArray();
        return headerAttributes.Length > 0 ? string.Join(", ", headerAttributes.Select(attr => attr.header)) : "";
    }

    private static void SaveReport(List<AssetPropertyInfo> report)
    {
        var path = EditorUtility.SaveFilePanel("Save Report", "", "CustomAssetPropertyReport.json", "json");
        if (string.IsNullOrEmpty(path)) return;

        var json = JsonUtility.ToJson(new ReportWrapper { Assets = report }, true);
        File.WriteAllText(path, json);
        EditorUtility.DisplayDialog("Report Generated", "The report has been generated successfully.", "OK");
    }

    [Serializable]
    public class AssetPropertyInfo
    {
        public string AssetType;
        public List<PropertyInfoWrapper> Properties;
    }

    [Serializable]
    public class PropertyInfoWrapper
    {
        public string Name;
        public string Type;
        public string Description;
        public string Group;
        public List<PropertyInfoWrapper> Children; // Added to hold child properties
    }

    [Serializable]
    public class ReportWrapper
    {
        public List<AssetPropertyInfo> Assets;
    }
}
