#!/bin/bash

brew-sync() {
    if [[ "$1" == "--cleanup" ]]; then
        echo -n "Are you sure you want to run brew cleanup? (y/N) "
        read confirm
        if [[ "$confirm" =~ ^[Yy]$ ]]; then

            # Check for orphaned MAS apps
            echo "Checking for orphaned MAS apps..."
            mas_list=$(mas list | awk '{print $1}')
            brew_mas_list=$(brew bundle dump --file=/dev/stdout | grep "^mas " | awk '{print $2}')

            orphaned_mas=()
            for app in $mas_list; do
                if ! echo "$brew_mas_list" | grep -q "$app"; then
                    orphaned_mas+=("$app")
                fi
            done

            if [[ ${#orphaned_mas[@]} -gt 0 ]]; then
                echo "⚠️  Orphaned MAS apps detected:"
                for app in "${orphaned_mas[@]}"; do
                    echo "  - $(mas info "$app" | head -1)"
                done
                echo -n "Do you want to remove these orphaned MAS apps? (y/N) "
                read remove_mas
                if [[ "$remove_mas" =~ ^[Yy]$ ]]; then
                    for app in "${orphaned_mas[@]}"; do
                        mas uninstall "$app"
                    done
                    echo "✅ Orphaned MAS apps removed."
                else
                    echo "Skipping MAS orphan removal."
                fi
            else
                echo "✅ No orphaned MAS apps found."
            fi

            # Run brew cleanup
            time brew bundle --global --quiet --cleanup
        else
            echo "Cleanup canceled."
        fi
    else
        time brew bundle --global --quiet
    fi
}