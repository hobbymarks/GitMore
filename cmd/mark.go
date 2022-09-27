/*
Copyright © 2022 NAME HERE <EMAIL ADDRESS>
*/
package cmd

import (
	"fmt"

	log "github.com/sirupsen/logrus"
	"github.com/spf13/cobra"
)

// markCmd represents the mark command
var markCmd = &cobra.Command{
	Use:   "mark",
	Short: "Mark some git repo directory",
	Long:  ``,
	Run: func(cmd *cobra.Command, args []string) {
		freeze, err := cmd.Flags().GetBool("freeze")
		if err != nil {
			log.Fatal(err)
		}
		unfreeze, err := cmd.Flags().GetBool("unfreeze")
		if err != nil {
			log.Fatal(err)
		}
		if !freeze && !unfreeze {
			fmt.Println("Please set one flag 'freeze(z)' or 'unfreeze(u)'")
			return
		}
		if freeze && unfreeze {
			fmt.Println("Please set only one flag 'freeze(z)' or 'unfreeze(u)'")
			return
		}
		if freeze {
			for _, arg := range args {
				if err := FreezeGitDir(arg); err != nil {
					log.Error(err)
				}
			}
		}
		if unfreeze {
			for _, arg := range args {
				if err := UnfreezeGitDir(arg); err != nil {
					log.Error(err)
				}
			}
		}
	},
}

func init() {
	rootCmd.AddCommand(markCmd)

	markCmd.Flags().BoolP("freeze", "z", false, "Freeze git dir")
	markCmd.Flags().BoolP("unfreeze", "u", false, "Unfreeze git dir")
}
