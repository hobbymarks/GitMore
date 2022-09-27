/*
Copyright © 2022 NAME HERE <EMAIL ADDRESS>
*/
package cmd

import (
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
		} else if !freeze {
			return
		}
		for _, arg := range args {
			if err := FreezeGitDir(arg); err != nil {
				log.Error(err)
			}
		}
	},
}

func init() {
	rootCmd.AddCommand(markCmd)

	markCmd.Flags().BoolP("freeze", "z", false, "Freeze git dir")
}
