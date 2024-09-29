import os
import shutil
import xml.etree.ElementTree as ET


def update_logback_xml(file_path):
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()

        for property in root.findall("property"):
            if property.get("name") == "logOutputPath":
                root.remove(property)

        # Find all 'appender' elements with name="FILE" and class="ch.qos.logback.core.rolling.RollingFileAppender"
        for appender in root.findall("appender"):
            if appender.get("class") == "ch.qos.logback.core.rolling.RollingFileAppender":
                # Modify the appender to use a console logger
                appender.set("class", "ch.qos.logback.core.ConsoleAppender")

                # Remove any <file> element inside the appender (specific to file logging)
                file_element = appender.find("file")
                if file_element is not None:
                    appender.remove(file_element)

                # Remove any <rollingPolicy> element inside the appender (specific to file logging)
                rolling_policy = appender.find("rollingPolicy")
                if rolling_policy is not None:
                    appender.remove(rolling_policy)

                # Check if an existing <encoder> element is present, or create a new one
                encoder = appender.find("encoder")
                if encoder is None:
                    encoder = ET.SubElement(appender, "encoder")

                # Add <pattern> element inside the <encoder> to format the console output
                pattern = encoder.find("pattern")
                if pattern is None:
                    pattern = ET.SubElement(encoder, "pattern")
                pattern.text = "%d{HH:mm:ss.SSS} %-5level %logger{36} - %msg%n"

                print(f"Updated: {file_path}")

        # Write the changes back to the XML file (in place modification)
        tree.write(file_path, encoding="utf-8", xml_declaration=True)
        print(f"Updated {file_path}")
        print(ET.tostring(root, encoding="utf-8").decode())

    except ET.ParseError as e:
        print(f"Failed to parse {file_path}: {e}")
    except Exception as e:
        print(f"Error updating {file_path}: {e}")


def update_logback_in_folder(folder_path):
    # Traverse through all the files in the folder
    for root, dirs, files in os.walk(folder_path):
        for file_name in files:
            if file_name.endswith("logback.xml") or file_name.endswith("logback-service.xml"):
                file_path = os.path.join(root, file_name)
                update_logback_xml(file_path)


def gather_install_files():
    """
    Gathers all the *.install files under the specified path, reads the lines from the files,
    and appends them to a list.
    """
    install_files = []
    for root, dirs, files in os.walk("./packages/src/xroad/ubuntu/generic"):
        for file in files:
            if file.endswith(".install"):
                with open(os.path.join(root, file), "r") as f:
                    install_files.extend(f.readlines())
    return install_files

def gather_service_files():
    """
    Gathers all the *.service files under the specified path, reads the lines from the files,
    and appends them to a list.
    """
    service_files = []
    for root, dirs, files in os.walk("./packages/src/xroad/ubuntu/generic"):
        for file in files:
            if file.endswith(".service"):
                with open(os.path.join(root, file), "r") as f:
                    service_files.extend(f.readlines())
    return service_files

def gather_links_files():
    """
    Gathers all the *.links files under the specified path, reads the lines from the files,
    and appends them to a list.
    """
    links_files = []
    for root, dirs, files in os.walk("./packages/src/xroad/ubuntu/generic"):
        for file in files:
            if file.endswith(".links"):
                with open(os.path.join(root, file), "r") as f:
                    links_files.extend(f.readlines())
    return links_files

def gather_nginx_files():
    """
    Gathers all the *.conf files under the specified
    path, reads the lines from the files, and appends them to a list.
    """
    nginx_files = []
    for root, dirs, files in os.walk("/etc/xroad/nginx"):
        for file in files:
            if file.endswith(".conf"):
                with open(os.path.join(root, file), "r") as f:
                    nginx_files.extend(f.readlines())
    return nginx_files

def copy_files(source, target):
    """
    Copies the source files to the target location.
    Handles both directories (with wildcard '*') and individual files.
    """
    if not target.startswith("/"):
        target = "/" + target

    # Handle directory copying (when source ends with '*')
    if source.endswith("*") or os.path.isdir(source):
        # Remove the '*' and copy the contents of the directory
        source = source[:-1]

        if os.path.isdir(source):
            # Ensure target directory exists
            os.makedirs(target, exist_ok=True)
            print(f"Copying contents of directory {source} to {target}")

            # Copy each item in the source directory to the target directory
            for item in os.listdir(source):
                s_item = os.path.join(source, item)
                t_item = os.path.join(target, item)
                if os.path.isdir(s_item):
                    shutil.copytree(
                        s_item, t_item, dirs_exist_ok=True
                    )  # copies subdirectories
                else:
                    shutil.copy2(s_item, t_item)  # copies files
        else:
            print(f"Source {source} is not a valid directory.")
    else:
        # Source is a file, copy the file to the target directory
        # If target is a directory, append the filename to the target path
        if os.path.isdir(target):
            target = os.path.join(target, os.path.basename(source))

        # Ensure the target directory exists
        target_dir = os.path.dirname(target)  # Extract the target directory
        print(f"Source file: {source}")
        target_file = target_dir + "/" + os.path.basename(source)
        print(f"Source file: {target_file}")
        print(f"Target directory: {target_dir}")
        print(f"Creating target directory {target_dir}")
        # Check if the target directory exists, if not create it
        if os.path.exists(target_dir):
            shutil.copy(source, target_file)
        else:
            os.makedirs(target_dir, exist_ok=True)

        # Perform the file copy
        shutil.copy(source, target_file)
        print(f"Copied {source} to {target}")

def symlinkfile(source, target):
    """
    Creates a symbolic link to the source file in the target directory.
    """
    if not target.startswith("/"):
        target = "/" + target
    
    if not source.startswith("/"):
        source = "/" + source

    if source.startswith("/etc/xroad/nginx/"):
        print(f"Skipping nginx symbolic link creation for {source} to {target}")
        return
    else:
        # Create the symbolic link
        print(f"Creating symbolic link from {source} to {target}")
        os.symlink(source, target)

if __name__ == "__main__":
    install_files = gather_install_files()
    service_files = gather_service_files()
    links_files = gather_links_files()
    xroad_src = "/src/X-Road-7.5.1/"

    # Get the services to create k8s deployment files
    for line in service_files:
        if line.startswith("Description"):
            print(line)
        if line.startswith("ExecStart"):
            print(line)

    # targets = []
    # for line in install_files:
    #     if line.strip() == "":
    #         continue
    #     target = line.split()[1]
    #     if (
    #         target.startswith("usr/share/xroad")
    #         or target.startswith("etc/xroad/")
    #         or target.startswith("/etc/xroad/")
    #         or target.startswith("usr/share/doc/")
    #         or target.startswith("/usr/share/xroad/")
    #     ):
    #         continue
    #     targets.append(line)
    # # Print the unique targets
    # unique_targets = set(targets)
    # for target in unique_targets:
    #     print(target)

    # For each line in the list, copy the file to the target directory
    for line in install_files:
        # Skip empty lines
        if line.strip() == "":
            continue

        source = line.split()[0]

        # Adjust the source paths
        if source.startswith("../../../../src/xroad/"):
            source = source.replace(
                "../../../../src/xroad/", xroad_src + "src/packages/src/xroad/"
            )
        elif source.startswith("../../../../../../"):
            source = source.replace("../../../../../../", xroad_src)
        elif source.startswith("../../../../../"):
            source = source.replace("../../../../../", xroad_src + "src/")

        # Set the target path
        target = line.split()[1]

        # Call the copy_files function to handle the copying process
        copy_files(source, target)

    # Links files
    for line in links_files:
        # Skip empty lines
        if line.strip() == "":
            continue
        source = line.split()[0]
        target = line.split()[1]
        symlinkfile(source, target)

    # Find all logback.xml files and update them
    update_logback_in_folder("/etc/xroad/conf.d")

    # print nginx files
    # nginx_files = gather_nginx_files()
    # for line in nginx_files:
    #     print(line)
